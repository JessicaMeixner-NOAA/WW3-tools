import datetime as dt
from dateutil.relativedelta import relativedelta
import os

rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'jobinterp')

season=['winter', 'summer', 'hurricane']
satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT
#model=['multi1', 'GFSv16', 'HR1', 'HR2', 'HR3']
model='HR1'

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
   outfile = os.path.join(rootdir, f"submit_{model}_{season[k]}.sh")
   with open(outfile, 'w') as f:
     for i in range(len(dates1)):
                sbatch = f"""sbatch job_{model}_{season[k]}_{dates1[i]}.sh
"""

                f.write(sbatch)



#/work/noaa/marine/jmeixner/Data/multi1/2019120300
#multi_1.ak_10m.t00z.f180.grib2	multi_1.glo_30mext.t00z.f180.grib2
#multi_1.ak_4m.t00z.f180.grib2	multi_1.glo_30m.t00z.f180.grib2    
#multi_1.at_10m.t00z.f180.grib2	multi_1.wc_10m.t00z.f180.grib2	    
#multi_1.at_4m.t00z.f180.grib2	multi_1.wc_4m.t00z.f180.grib2	     
#multi_1.ep_10m.t00z.f180.grib2	




