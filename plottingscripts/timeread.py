import datetime
import numpy as np
import netCDF4 as nc

start = datetime.date(2019, 12, 3)
end = datetime.date(2020, 2, 25)
end = datetime.date(2019, 12, 6)
res_date = start
folderpath='/work/noaa/marine/jmeixner/2020091300'
model='HR3ascout'
satname='JASON3'
time=[]
lats=[]
lons=[]
obs_hs=[]
obs_wnd=[]
model_hs=[]
model_wnd=[]
fhr=[]
while res_date <= end:
    year=res_date.strftime("%Y")
    month=res_date.strftime("%m")
    day=res_date.strftime("%d")
    cdate=year+month+day+'00'
    print("cdate=",cdate)
    filepath=folderpath+'/'+model+'_'+satname+'_'+cdate+'.nc' 
    print(filepath)

    datanc  = nc.Dataset(filepath)
    validtime = np.array(datanc.variables['time'][:]).astype('double')
    lat  = np.array(datanc.variables['latitude'][:])
    lon  = np.array(datanc.variables['longitude'][:])
    obshs = np.array(datanc.variables['hs'][:])
    obswnd = np.array(datanc.variables['wsp_cal'][:])
    modelhs = np.array(datanc.variables['swh_interpolated'][:])
    modelwnd = np.array(datanc.variables['ws_interpolated'][:]) 

    #print('validtime=',validtime)
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')
 
    fhrs=np.array((validtime-refcdate)/3600)
    #print('fhrmin',np.min(fhrs)) 
    #print('fhrmax',np.max(fhrs)) 
    #howmanyhours=(np.max(validtime)-np.min(validtime))/3600 
    #print('howmanyhours',howmanyhours)

    time=np.append(time,validtime)
    lats=np.append(lats,lat)
    lons=np.append(lons,lon)
    obs_hs=np.append(obs_hs,obshs)
    obs_wnd=np.append(obs_wnd,obswnd)
    model_hs=np.append(model_hs,modelhs)
    model_wnd=np.append(model_wnd,modelwnd)
    fhr=np.append(fhr,fhrs)

    res_date += datetime.timedelta(days=3)


