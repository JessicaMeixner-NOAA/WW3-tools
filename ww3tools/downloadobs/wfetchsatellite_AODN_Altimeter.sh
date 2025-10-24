#!/bin/bash

# wfetchsatellite_AODN_Altimeter_parallel.sh
# Optimized & parallelized version of wfetchsatellite_AODN_Altimeter.sh
# - Builds a list of missing files and downloads them in parallel (xargs or GNU parallel)
# - Avoids repeated filesystem checks inside tight loops
# - Uses wget with resume and limited retries
# - Cleans up partial empty files at the end
#
# Usage:
#  bash wfetchsatellite_AODN_Altimeter_parallel.sh SATELLITE DEST_DIR HEMI [CONCURRENCY] [BACKEND]
#  example (use xargs, 8 jobs):    bash wfetchsatellite_AODN_Altimeter_parallel.sh CRYOSAT-2 /data/AODN_altm S 8 xargs
#  example (use GNU parallel):     bash wfetchsatellite_AODN_Altimeter_parallel.sh CRYOSAT-2 /data/AODN_altm S 8 parallel
#  example (auto-detect backend):  bash wfetchsatellite_AODN_Altimeter_parallel.sh CRYOSAT-2 /data/AODN_altm S 8 auto
#  example (serial):               bash wfetchsatellite_AODN_Altimeter_parallel.sh CRYOSAT-2 /data/AODN_altm S 0 serial
#
# Notes:
#  - BACKEND values: auto (default), xargs, parallel, serial
#  - Default concurrency = 8 (tweak for your network / server limits)
#  - If BACKEND=auto, the script prefers GNU parallel if available, otherwise xargs, otherwise falls back to serial
#  - The script preserves the original filename saved by the AODN server
#  - After run it will produce listDownloaded_<SAT>.txt and listFailed_<SAT>.txt in the destination dir
#
# Author: Adapted from Ricardo M. Campos script
# Date: 2025-10-22 (updated 2025-10-23 to add GNU parallel option)

set -eu -o pipefail

BASE_URL="http://thredds.aodn.org.au/thredds/fileServer/IMOS/SRS/Surface-Waves/Wave-Wind-Altimetry-DM00"

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 SATELLITE DEST_DIR HEMI [CONCURRENCY] [BACKEND]"
  echo "Example: $0 CRYOSAT-2 /data/AODN_altm S 8 parallel"
  exit 2
fi

s="$1"
DIR="$2"
h="$3"
CONC="${4:-8}"                           # parallel jobs (0 treated as serial)
BACKEND="${5:-auto}"                     # auto, xargs, parallel, serial

mkdir -p "$DIR"

TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT

# build list of URLs to download (only if local file missing and not previously failed)
failed_list="${DIR}/listFailed_${s}.txt"

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

        # Only add to download list if local file is missing AND the filename is not listed in listFailed_<sat>.txt
        if [ ! -f "$target" ]; then
          if [ -f "$failed_list" ] && grep -Fxq "$filename" "$failed_list"; then
            # previously failed - skip (do not add to TMP_LIST)
            :
          else
            echo "$url" >> "$TMP_LIST"
          fi
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

# Decide backend if auto
actual_backend="$BACKEND"
if [ "$BACKEND" = "auto" ]; then
  if command -v parallel >/dev/null 2>&1; then
    actual_backend="parallel"
  elif command -v xargs >/dev/null 2>&1; then
    actual_backend="xargs"
  else
    actual_backend="serial"
  fi
fi

echo "Will download ${num_to_get} files with concurrency=${CONC}, backend=${actual_backend}..."

export DIR s

download_worker() {
  local url="$1"
  local filename="${url##*/}"

  if wget -c -q --timeout=30 --tries=3 -P "$DIR" "$url"; then
    echo "$filename" >> "${DIR}/listDownloaded_${s}.txt"
    # If it previously failed and now succeeded, remove it from failed list (best-effort)
    if [ -f "${DIR}/listFailed_${s}.txt" ]; then
      # create a temp file and avoid failing the script if grep returns non-zero
      grep -Fvx "$filename" "${DIR}/listFailed_${s}.txt" > "${DIR}/listFailed_${s}.txt.tmp" || true
      mv "${DIR}/listFailed_${s}.txt.tmp" "${DIR}/listFailed_${s}.txt"
    fi
  else
    echo "$filename" >> "${DIR}/listFailed_${s}.txt"
  fi
}

export -f download_worker

case "$actual_backend" in
  parallel)
    if ! command -v parallel >/dev/null 2>&1; then
      echo "GNU parallel requested but not found in PATH. Falling back to xargs or serial."
      if command -v xargs >/dev/null 2>&1; then
        actual_backend="xargs"
      else
        actual_backend="serial"
      fi
    fi
    ;;
esac

case "$actual_backend" in
  parallel)
    # Use GNU parallel. Pass each URL to download_worker via bash -c so the exported function is available.
    # -a reads input file, -j sets job count, --no-notice suppresses the citation notice.
    if [ "$CONC" -le 0 ]; then
      # treat non-positive concurrency as serial when using parallel
      while IFS= read -r url; do
        download_worker "$url"
      done < "$TMP_LIST"
    else
      parallel -a "$TMP_LIST" -j "$CONC" --no-notice bash -c 'download_worker "$@"' _ {}
    fi
    ;;
  xargs)
    # Use xargs with -P for parallel execution. xargs -a is POSIX-ish and reads from file.
    if [ "$CONC" -le 0 ]; then
      while IFS= read -r url; do
        download_worker "$url"
      done < "$TMP_LIST"
    else
      xargs -a "$TMP_LIST" -n1 -P "$CONC" -I{} bash -c 'download_worker "$@"' _ {}
    fi
    ;;
  serial)
    # Serial fallback (no parallelism)
    while IFS= read -r url; do
      download_worker "$url"
    done < "$TMP_LIST"
    ;;
  *)
    echo "Unknown backend: ${actual_backend}. Supported: auto, parallel, xargs, serial"
    exit 3
    ;;
esac

# cleanup empty files (possibly left by interrupted downloads)
find "$DIR" -empty -type f -delete

echo ""
echo "Done. Downloaded list: ${DIR}/listDownloaded_${s}.txt"
echo "Failed list: ${DIR}/listFailed_${s}.txt (if any)"
exit 0
