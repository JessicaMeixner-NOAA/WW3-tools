import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import argparse

import datetime as dt
from dateutil.relativedelta import relativedelta
import os
import xarray as xr


'''
Create combined NetCDF files for easier post processing. 
'''

def main():

  ap = argparse.ArgumentParser()
  ap.add_argument('-o', '--outdir', help="Output directory for files", default='./')
  MyArgs = ap.parse_args()

  OUTDIR = MyArgs.outdir


  #Check output directory exists: 
  INPUTDIR=f"/work2/noaa/marine/ming.chen/GFS_Retro_Data/data/outinterp"

  if not os.path.isdir(INPUTDIR):
    INPUTDIR=f"/scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/outinterp"
    if not os.path.isdir(INPUTDIR):
      print('INPUTDIR ({INPUTDIR}) does not exist!!!!') 
      exit(1) 

  #create OUTDIR directory if it does not exist: 
  if not os.path.isdir(OUTDIR):
    os.makedirs(OUTDIR)


  import datetime as dt

  # Define your configuration mapping
  STREAM_CONFIGS = {
    "stream1a": {"start": dt.datetime(2022, 8, 30, 12), "end": dt.datetime(2022, 10, 15, 18), "stride": 6},
    "test":     {"start": dt.datetime(2024, 11, 9),      "end": dt.datetime(2024, 11, 15, 18), "stride": 6},
    "stream1b": {"start": dt.datetime(2024, 3, 1),      "end": dt.datetime(2024, 5, 31, 18),  "stride": 12},
    "stream2":  {"start": dt.datetime(2024, 6, 1),      "end": dt.datetime(2024, 11, 30, 18), "stride": 6},
    "stream2a": {"start": dt.datetime(2024, 6, 1),      "end": dt.datetime(2024, 8, 31, 18),  "stride": 6},
    "stream2b": {"start": dt.datetime(2024, 9, 1),      "end": dt.datetime(2024, 11, 30, 18), "stride": 6},
    "stream3":  {"start": dt.datetime(2024, 12, 1),     "end": dt.datetime(2025, 5, 31, 18),  "stride": 12},
    "stream3a": {"start": dt.datetime(2024, 12, 1),     "end": dt.datetime(2025, 2, 28, 18),  "stride": 12},
    "stream3b": {"start": dt.datetime(2024, 3, 1),      "end": dt.datetime(2025, 5, 31, 18),  "stride": 12},
    "stream4":  {"start": dt.datetime(2025, 6, 1),      "end": dt.datetime(2025, 11, 30, 18), "stride": 6},
    "stream4a": {"start": dt.datetime(2025, 6, 1),      "end": dt.datetime(2025, 8, 31, 18),  "stride": 6},
    "stream4b": {"start": dt.datetime(2025, 9, 1),      "end": dt.datetime(2025, 11, 30, 18), "stride": 6},
    "realtime": {"start": dt.datetime(2025, 12, 1),      "end": dt.datetime(2026, 2, 28, 18), "stride": 6}
    }

  seasons = ['stream1a', 'stream1b', 'stream2a', 'stream2b', 'stream3a', 'stream3b']
  #seasons = ['test']
  satelites = ['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A', 'SENTINEL3B', 'SENTINEL6A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT

  seasons = ['stream1a']
  satelites = ['JASON3']
    
  # 2. Iterate directly over the list (avoid range(len()))
  for season in seasons:
    config = STREAM_CONFIGS.get(season)
    if config:
      startdate = config["start"]
      enddate = config["end"]
      hourstride = config["stride"]
        
      nowdate = startdate
      dates1 = []
      while nowdate <= enddate:
        dates1.append(nowdate.strftime('%Y%m%d%H'))
        nowdate = nowdate + dt.timedelta(hours=hourstride)
      print(dates1)
    for j in range(len(satelites)): 
      time = []; lats = []; lons = []
      fhrs = []; fhrsall = [];
      obs_hs = []; obs_wnd = []
      model_hs = []; model_wnd = []
      ops_hs = []; ops_wnd = []
      obs_hs_cal = []; obs_wnd_cal = []
      for i in range(len(dates1)):
         #list of grids for each model.  First should be "global" or the base, followed by high resolution inserts in the order 
         #of lower(global) to higher(regional) resolution. 
         grids='global.0p25'

         #read ops data: 
         model_ops='GFSv16'
         INPUT_FILE_ops=f"{model_ops}_{grids}_{dates1[i]}_{satelites[j]}.nc"

         datapath = INPUTDIR + "/" + model_ops + "/" + INPUT_FILE_ops
         if os.path.isfile(datapath):
           datanc  = nc.Dataset(datapath)

           time_tmpbase_ops = np.array(datanc.variables['time'][:])
           fhrs_tmpbase_ops = np.array(datanc.variables['fcst_hr'][:])
           lats_tmpbase_ops = np.array(datanc.variables['latitude'][:])
           lons_tmpbase_ops = np.array(datanc.variables['longitude'][:])
           obs_hs_tmpbase_ops = np.array(datanc.variables['obs_hs'][:])
           obs_hs_cal_tmpbase_ops = np.array(datanc.variables['obs_hs_cal'][:])
           obs_wnd_tmpbase_ops = np.array(datanc.variables['obs_wnd'][:])
           obs_wnd_cal_tmpbase_ops = np.array(datanc.variables['obs_wnd_cal'][:])
           model_hs_tmpbase_ops = np.array(datanc.variables['model_hs'][:])
           model_wnd_tmpbase_ops = np.array(datanc.variables['model_wnd'][:]) 
           initial_condition_time_ops = datanc.getncattr('initial_condition_time')
           fhrsall_tmpbase_ops = (time_tmpbase_ops - initial_condition_time_ops)/3600

           #read v17 data 
           model_v17='retrov17_01'
           INPUT_FILE=f"{model_v17}_{grids}_{dates1[i]}_{satelites[j]}.nc"

           datapath = INPUTDIR + "/" + model_v17 + "/" + INPUT_FILE
           if os.path.isfile(datapath):
             datanc  = nc.Dataset(datapath)

             time_tmpbase = np.array(datanc.variables['time'][:])
             fhrs_tmpbase = np.array(datanc.variables['fcst_hr'][:])
             lats_tmpbase = np.array(datanc.variables['latitude'][:])
             lons_tmpbase = np.array(datanc.variables['longitude'][:])
             obs_hs_tmpbase = np.array(datanc.variables['obs_hs'][:])
             obs_hs_cal_tmpbase = np.array(datanc.variables['obs_hs_cal'][:])
             obs_wnd_tmpbase = np.array(datanc.variables['obs_wnd'][:])
             obs_wnd_cal_tmpbase = np.array(datanc.variables['obs_wnd_cal'][:])
             model_hs_tmpbase = np.array(datanc.variables['model_hs'][:])
             model_wnd_tmpbase = np.array(datanc.variables['model_wnd'][:])
             initial_condition_time = datanc.getncattr('initial_condition_time')
             fhrsall_tmpbase = (time_tmpbase - initial_condition_time)/3600

 
             #Check that obs values are the same for sanity check
             if ((obs_hs_tmpbase_ops == obs_hs_tmpbase).all()): 
               if ((lons_tmpbase == lons_tmpbase_ops).all()): 
                 # Find where both models are not nan  
                 mask = ~np.isnan(model_hs_tmpbase) & ~np.isnan(model_hs_tmpbase_ops)
               
                 time = np.append(time, time_tmpbase[mask]) 
                 lats = np.append(lats, lats_tmpbase[mask])
                 lons = np.append(lons, lons_tmpbase[mask])
                 fhrs = np.append(fhrs, fhrs_tmpbase[mask])
                 fhrsall = np.append(fhrsall, fhrsall_tmpbase[mask])

                 obs_hs = np.append(obs_hs, obs_hs_tmpbase[mask])
                 obs_wnd = np.append(obs_wnd, obs_wnd_tmpbase[mask])
                 obs_hs_cal = np.append(obs_hs_cal, obs_hs_cal_tmpbase[mask])
                 obs_wnd_cal = np.append(obs_wnd_cal, obs_wnd_cal_tmpbase[mask])

                 model_hs = np.append(model_hs, model_hs_tmpbase[mask])
                 model_wnd = np.append(model_wnd, model_wnd_tmpbase[mask])

                 ops_hs = np.append(ops_hs, model_hs_tmpbase_ops[mask])
                 ops_wnd = np.append(ops_wnd, model_wnd_tmpbase_ops[mask])
               else: 
                 print(f"lons diff for {dates1[i]} {satelites[j]}")
             else: 
               print(f"hs obs diff for {dates1[i]} {satelites[j]}")
           else: 
             print(f"{datapath} does not exist") 
         else: 
           print(f"{datapath} does not exist")
      #Call function to write out netcdf file with all forecast hours
      outfilename=f"combined_{season}_{satelites[j]}.nc"
      OUTFILE = OUTDIR + '/' + outfilename 
      write_netcdf_file(OUTFILE, satelites[j], time,lats, lons, fhrs, obs_hs, obs_hs_cal, obs_wnd, obs_wnd_cal, model_hs, model_wnd, ops_hs, ops_wnd)

def write_netcdf_file(nameoffile,nameofsat, val_time, val_lats, val_lons, val_fhrs, val_obs_hs, val_obs_hs_cal, val_obs_wnd, val_obs_wnd_cal, val_model_hs, val_model_wnd, val_ops_hs, val_ops_wnd): 

        time_dataarray = xr.DataArray(val_time, dims=['time'], name='time', attrs={
           'standard_name': 'time',
           'units': 'seconds since 1970-01-01 00:00:00',
           'calendar': 'standard',
           'axis': 'T'
        })

        interpolated_dataset = xr.Dataset({
           'time': time_dataarray,
           'latitude': xr.DataArray(val_lats, coords={'time': val_time}, dims=['time'], name='latitude').assign_attrs(units='degree_north'),
           'longitude': xr.DataArray(val_lons, coords={'time': val_time}, dims=['time'], name='longitude').assign_attrs(units='degree_east'),
           'model_hs': xr.DataArray(val_model_hs, coords={'time': val_time}, dims=['time'], name='model_hs').assign_attrs(units='m'),
           'model_wnd': xr.DataArray(val_model_wnd, coords={'time': val_time}, dims=['time'], name='model_wnd').assign_attrs(units='m'),
           'ops_hs': xr.DataArray(val_model_hs, coords={'time': val_time}, dims=['time'], name='ops_hs').assign_attrs(units='m'),
           'ops_wnd': xr.DataArray(val_model_wnd, coords={'time': val_time}, dims=['time'], name='ops_wnd').assign_attrs(units='m'),
           'obs_hs': xr.DataArray(val_obs_hs, coords={'time': val_time}, dims=['time'], name='obs_hs').assign_attrs(units='m'),
           'obs_hs_cal': xr.DataArray(val_obs_hs_cal, coords={'time': val_time}, dims=['time'], name='obs_hs_cal').assign_attrs(units='m'),
           'obs_wnd': xr.DataArray(val_obs_wnd, coords={'time': val_time}, dims=['time'], name='obs_wnd').assign_attrs(units='m/s'),
           'obs_wnd_cal': xr.DataArray(val_obs_wnd_cal, coords={'time': val_time}, dims=['time'], name='obs_wnd_cal').assign_attrs(units='m/s'),
           'fcst_hr': xr.DataArray(val_fhrs,coords={'time': val_time}, dims=['time'], name='fcst_hr').assign_attrs(description="Forecast hour relative to initial condition time", units='hours')
        })

        interpolated_dataset.attrs['satellite_name'] = f"{nameofsat}"
        interpolated_dataset.to_netcdf(nameoffile, format='NETCDF4')


if __name__ == '__main__':
    main()
