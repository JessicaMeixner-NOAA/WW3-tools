import datetime as dt
from dateutil.relativedelta import relativedelta
import os

rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'tempsub')

season=['winter', 'summer', 'hurricane']
satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
#model=['multi1', 'GFSv16', 'HR1', 'HR2', 'HR3a']
model='HR2'
for k in range(len(season)):
   if season[k] == "winter":
       startdate = dt.datetime(2019,12,3)
       enddate = dt.datetime(2020,2,26)
       datestride = 3 
   elif season[k] == "summer":
       startdate = dt.datetime(2020,6,1)
       enddate = dt.datetime(2020,8,30)
       datestride = 3
   elif season[k] == "hurricane":
       startdate = dt.datetime(2020,7,20)
       enddate = dt.datetime(2020,11,20)
       datestride = 1 

   nowdate = startdate
   dates1 = []
   while nowdate <= enddate:
       dates1.append(nowdate.strftime('%Y%m%d%H'))
       #nowdate = (nowdate + dt.timedelta(days=datestride)).strftime('%Y%m%d') 
       nowdate = nowdate + dt.timedelta(days=datestride)
    
   print(dates1)
   for i in range(len(dates1)):
        for j in range(len(satelites)): 
            outfile = os.path.join(rootdir, f"job_{model}_{satelites[j]}_{season[k]}_{dates1[i]}.sh")
            with open(outfile, 'w') as f:
                f.write('#!/bin/bash\n')
                sbatch = f"""#SBATCH --nodes=1
#SBATCH -q batch
#SBATCH -t 08:00:00
#SBATCH -A marine-cpu
#SBATCH -J procsat_{model}_{satelites[j]}_{season[k]}_{dates1[i]}
#SBATCH -o run_{model}_{satelites[j]}_{season[k]}_{dates1[i]}.o%j
#SBATCH --partition=orion
#SBATCH --exclusive


module use /work2/noaa/marine/jmeixner/general/modulefiles
module load ww3tools

ThisDir=/work2/noaa/marine/jmeixner/processsatdata
PathToWW3TOOLS=/work2/noaa/marine/jmeixner/processsatdata/ww3-tools/ww3tools

SAT={satelites[j]}
SEASON={season[k]}
MODEL={model}
CDATE={dates1[i]}
OUTDIR=/work2/noaa/marine/jmeixner/processsatdata/outinterp/{model} 

"""

                f.write(sbatch)
                f.write('SATELLITE_FILE=/work/noaa/marine/jmeixner/Data/processedsatdata/Altimeter_${SAT}_HR${SEASON}.nc \n')
                f.write('DATE=${CDATE:0:8} \n') 
                f.write('TZ=${CDATE:8:2} \n') 
                f.write('MODEL_DATA_DIR="/work/noaa/marine/jmeixner/Data/${MODEL}/${SEASON}/gfs.${DATE}/${TZ}/wave/gridded" \n') 
                f.write("MODEL_DATA_PATTERN='gfswave.t00z.global.0p25.f*.grib2'\n") 
                f.write('OUTPUT_FILE="${MODEL}_global.0p25_${SEASON}_${CDATE}_${SAT}.nc" \n')
                f.write('python ${PathToWW3TOOLS}/ProcSat_interpolation.py -t grib2 -d $MODEL_DATA_DIR -p $MODEL_DATA_PATTERN -s $SATELLITE_FILE -o $OUTDIR -f $OUTPUT_FILE -m ${MODEL} \n')
               

