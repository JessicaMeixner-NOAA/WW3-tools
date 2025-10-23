#!/bin/bash

# wfetchsatellite_AODN_Altimeter_parallel.sh
# Optimized & parallelized version of wfetchsatellite_AODN_Altimeter.sh
# - Builds a list of missing files and downloads them in parallel (xargs or GNU parallel)
# - Avoids repeated filesystem checks inside tight loops
# - Uses wget with resume and limited retries
# - Cleans up partial empty files at the end
#
# Usage:
#  bash wfetchsatellite_AODN_Altimeter_parallel.sh SATELLITE DEST_DIR HEMI [CONCURRENCY]
#  example: bash wfetchsatellite_AODN_Altimeter_parallel.sh CRYOSAT-2 /data/AODN_altm S 8
#
# Notes:
#  - Requires: wget, xargs (most systems) or GNU parallel if you prefer to use it
#  - Default concurrency = 8 (tweak for your network / server limits)
#  - The script preserves the original filename saved by the AODN server
#  - After run it will produce listDownloaded_<SAT>.txt and listFailed_<SAT>.txt in the destination dir
#
# Author: Adapted from Ricardo M. Campos script
# Date: 2025-10-22

set -eu -o pipefail

BASE_URL="http://thredds.aodn.org.au/thredds/fileServer/IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00"

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 SATELLITE DEST_DIR HEMI [CONCURRENCY]"
  echo "Example: $0 CRYOSAT-2 /data/AODN_altm S 8"
  exit 2
fi

s="$1"
DIR="$2"
h="$3"
CONC="${4:-8}"   # parallel jobs

mkdir -p "$DIR"

TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT

# build list of URLs to download (only if local file missing)
for lon in $(seq -f "%03g" 0 20 340); do
  for lat in $(seq -f "%03g" 0 20 80); do
    for adlat in $(seq -f "%03g" 0 20); do
      lat_dec=$((10#$lat))
      adlat_dec=$((10#$adlat))
      if [[ "$h" == "N" ]]; then
        lat2_dec=$((lat_dec + adlat_dec))
      else
        lat2_dec=$((lat_dec - adlat_dec))
      fi
      if [ "$lat2_dec" -lt 0 ]; then
        lat2_abs=$(( -1 * lat2_dec ))
      else
        lat2_abs=$lat2_dec
      fi

      for adlon in $(seq -f "%03g" 0 19); do
        lon_dec=$((10#$lon))
        adlon_dec=$((10#$adlon))
        lon2_dec=$((lon_dec + adlon_dec))
        lat_field=$(printf "%03d" "$lat2_abs")
        lon_field=$(printf "%03d" "$lon2_dec")
        remote_dir="${lat}${h}_${lon}E"
        filename="IMOS_SRS-Surface-Waves_MW_${s}_FV02_${lat_field}${h}-${lon_field}E-DM00.nc"
        url="${BASE_URL}/${s}/${remote_dir}/${filename}"
        target="${DIR}/${filename}"

        if [ ! -f "$target" ]; then
          echo "$url" >> "$TMP_LIST"
        fi
      done
    done
  done
done

num_to_get=0
if [ -f "$TMP_LIST" ]; then
  num_to_get=$(wc -l < "$TMP_LIST" | tr -d ' ')
fi

if [ "$num_to_get" -eq 0 ]; then
  echo "No missing files for satellite ${s} in ${DIR}"
  exit 0
fi

echo "Will download ${num_to_get} files with concurrency=${CONC}..."

export DIR s

download_worker() {
  local url="$1"
  local filename="${url##*/}"

  if wget -c -q --timeout=30 --tries=3 -P "$DIR" "$url"; then
    echo "$filename" >> "${DIR}/listDownloaded_${s}.txt"
  else
    echo "$filename" >> "${DIR}/listFailed_${s}.txt"
  fi
}

export -f download_worker

if command -v xargs >/dev/null 2>&1; then
  gxargs -a "$TMP_LIST" -n1 -P "$CONC" -I{} bash -c 'download_worker "$@"' _ {}
else
  while IFS= read -r url; do
    download_worker "$url"
  done < "$TMP_LIST"
fi

# cleanup empty files (possibly left by interrupted downloads)
find "$DIR" -empty -type f -delete

echo ""
echo "Done. Downloaded list: ${DIR}/listDownloaded_${s}.txt"
echo "Failed list: ${DIR}/listFailed_${s}.txt (if any)"
exit 0

