import datetime as dt
from dateutil.relativedelta import relativedelta
import os

rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'jobinterp')

season=['winter', 'summer', 'hurricane']
satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
#model=['multi1', 'GFSv16', 'HR1', 'HR2', 'HR3a']
model='multi1'

for k in range(len(season)):
   if season[k] == "winter":
       startdate = dt.datetime(2019,12,3)
       enddate = dt.datetime(2020,2,20)
       datestride = 3 
   elif season[k] == "summer":
       startdate = dt.datetime(2020,6,1)
       #enddate = dt.datetime(2020,8,30) #nooverlap needed 
       enddate = dt.datetime(2020,7,19)
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
   outfile = os.path.join(rootdir, f"z_check_{model}_{season[k]}.sh")
   with open(outfile, 'w') as f:
     for i in range(len(dates1)):
                sbatch = f"""
SEASON={season[k]}
MODEL={model}
CDATE={dates1[i]}
OUTDIR=/work2/noaa/marine/jmeixner/processsatdata/outinterp/{model} 

"""

                f.write(sbatch)
                f.write('DATE=${CDATE:0:8} \n')
                f.write('TZ=${CDATE:8:2} \n')
                for j in range(len(satelites)):
                        satvalue = f"""

SAT={satelites[j]}

"""
                        f.write(satvalue)

                        grids=['glo_30m','ak_10m','at_10m','ep_10m','wc_10m','ak_4m','at_4m','wc_4m']
                        for g in range(len(grids)): 
                           if grids[g] == 'glo_30m':
                               f.write('OUTPUT_FILE="${MODEL}_global.0p50_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'ak_10m':
                               f.write('OUTPUT_FILE="${MODEL}_alaska.0p16_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'at_10m':
                               f.write('OUTPUT_FILE="${MODEL}_atlocn.0p16_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'ep_10m':
                               f.write('OUTPUT_FILE="${MODEL}_epacif.0p16_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'wc_10m':
                               f.write('OUTPUT_FILE="${MODEL}_wcoast.0p16_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'ak_4m':
                               f.write('OUTPUT_FILE="${MODEL}_alaska.0p06_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'at_4m':
                               f.write('OUTPUT_FILE="${MODEL}_atlocn.0p06_${CDATE}_${SAT}.nc" \n')
                           elif grids[g] == 'wc_4m':
                               f.write('OUTPUT_FILE="${MODEL}_wcoast.0p06_${CDATE}_${SAT}.nc" \n')
                           f.write('if ! [ -f ${OUTDIR}/${OUTPUT_FILE} ]; then \n')
                           f.write('  echo "File ${OUTPUT_FILE} does not exist." \n')
                           f.write('fi \n')







