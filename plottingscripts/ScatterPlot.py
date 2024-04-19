import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import argparse

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter
from emcpy.plots.plots import Scatter
from emcpy.plots.create_plots import CreatePlot, CreateFigure

import datetime as dt
from dateutil.relativedelta import relativedelta
import os

'''
ScatterPlot.py creates scatter density plots (model vs obs) by day for a model input for HR experiments and obs  
'''

def main():

  ap = argparse.ArgumentParser()
  ap.add_argument('-m', '--model', help="String Identifier of Model 'multi1', 'GFSv16', 'HR1', 'HR2', 'HR3a', 'HR3b'", required=True)
  MyArgs = ap.parse_args()

  model = MyArgs.model

  rootdir = os.path.join('/work2/noaa/marine/jmeixner/processsatdata', 'jobinterp')

  satelites=['JASON3', 'CRYOSAT2', 'SARAL', 'SENTINEL3A'] #JASON3,JASON2,CRYOSAT2,JASON1,HY2,SARAL,SENTINEL3A,ENVISAT,ERS1,ERS2,GEOSAT,GFO,TOPEX,SENTINEL3B,CFOSAT

  if model == "GFSv16": 
    season=['summer', 'hurricane']
  else: 
    season=['winter', 'summer', 'hurricane']


  for k in range(len(season)):
    if season[k] == "winter":
       startdate = dt.datetime(2019,12,3)
       enddate = dt.datetime(2020,2,20)
       datestride = 3 
       endday = 16
    elif season[k] == "summer":
       startdate = dt.datetime(2020,6,1)
       enddate = dt.datetime(2020,8,30)
       datestride = 3
       endday = 16
    elif season[k] == "hurricane":
       startdate = dt.datetime(2020,7,20)
       enddate = dt.datetime(2020,11,20)
       datestride = 1
       endday = 7

    nowdate = startdate
    dates1 = []
    while nowdate <= enddate:
       dates1.append(nowdate.strftime('%Y%m%d%H'))
       nowdate = nowdate + dt.timedelta(days=datestride)
    print(dates1)

    for j in range(len(satelites)): 
      time = []; lats = []; lons = []; fhrs = []
      obs_hs = []; obs_wnd = []; obscal_hs =[]; obscal_wnd = []
      model_hs = []; model_wnd = []
      for i in range(len(dates1)):
         OUTDIR=f"/work2/noaa/marine/jmeixner/processsatdata/outinterp/{model}" 
         if model == "multi1": 
            OUTPUT_FILE=f"{model}_global.0p50_{dates1[i]}_{satelites[j]}.nc"
         elif model == "GFSv16":
            OUTPUT_FILE=f"{model}_global.0p25_{dates1[i]}_{satelites[j]}.nc"
         else: 
            OUTPUT_FILE=f"{model}_global.0p25_{season[k]}_{dates1[i]}_{satelites[j]}.nc"
         datapath = OUTDIR + "/" + OUTPUT_FILE
         print(datapath)
         datanc  = nc.Dataset(datapath)

         #time = np.append(time, np.array(datanc.variables['time'][:]) 
         #lats = np.append(lats, np.array(datanc.variables['latitude'][:]))    
         #lons = np.append(lons, np.array(datanc.variables['longitude'][:])) 
         fhrs = np.append(fhrs, np.array(datanc.variables['fcst_hr'][:])) 

         obs_hs = np.append(obs_hs,np.array(datanc.variables['obs_hs'][:]))
         obs_wnd = np.append(obs_wnd, np.array(datanc.variables['obs_wnd_cal'][:]))
         #obscal_wnd = np.append(obscal_wnd, np.array(datanc.variables['obs_wnd_cal'][:]))
         #obscal_hs = np.append(obscal_hs, np.array(datanc.variables['model_hs_cal'][:]))

         model_hs = np.append(model_hs, np.array(datanc.variables['model_hs'][:]))
         model_wnd = np.append(model_wnd, np.array(datanc.variables['model_wnd'][:]))

      day0=0   
      day=1 
      while day <= endday:
        f0 = day0*24 
        f1 = day*24
        print(f0) 
        print(f1) 
        indx=np.where(( fhrs < f1 ) & ( fhrs > f0 ) & (~np.isnan(model_hs)) 
        obs_hs_day = obs_hs[indx]
        obs_wnd_day = obs_wnd[indx]
        model_hs_day = model_hs[indx]
        model_wnd_day = model_wnd[indx]

        # Create Scatter object
        sctr1 = Scatter(obs_hs_day, model_hs_day)
        sctr1.density_scatter()
        plot1 = CreatePlot()
        plot1.plot_layers = [sctr1]
        plot1.add_title(label=f"HS Day {day} {model} {satelites[j]} {season[k]}")
        plot1.add_xlabel(xlabel=f"observation ({satelites[j]})")
        plot1.add_ylabel(ylabel=f"model ({model})")
        plot1.add_legend()
        plot1.set_xlim(0,15) 
        plot1.set_ylim(0,15) 
        fig = CreateFigure()
        fig.plot_list = [plot1]
        fig.create_figure()
        fig.save_figure(f"scatter_HS_{model}_{satelites[j]}_{season[k]}_day{day}.png")
        fig.close_figure()    

        sctr1 = Scatter(obs_wnd_day, model_wnd_day)
        sctr1.density_scatter()
        plot1 = CreatePlot()
        plot1.plot_layers = [sctr1]
        plot1.add_title(label=f"WND Day {day} {model} {satelites[j]} {season[k]}")
        plot1.add_xlabel(xlabel=f"observation ({satelites[j]})")
        plot1.add_ylabel(ylabel=f"model ({model})")
        plot1.add_legend()
        plot1.set_xlim(0,35) 
        plot1.set_ylim(0,35) 
        fig = CreateFigure()
        fig.plot_list = [plot1]
        fig.create_figure()
        fig.save_figure(f"scatter_WND_{model}_{satelites[j]}_{season[k]}_day{day}.png")
        fig.close_figure()

        day0 = day
        day = day + 1


if __name__ == '__main__':
    main()
