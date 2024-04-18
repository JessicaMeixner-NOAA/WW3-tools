import datetime
import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter
from emcpy.plots.plots import Scatter
from emcpy.plots.create_plots import CreatePlot, CreateFigure


def main():
    # Create test data
    datapath='/work/noaa/marine/jmeixner/2020091300/HR3ascout_JASON3_2020091300.nc'
    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    lats  = np.array(datanc.variables['latitude'][:])
    lons  = np.array(datanc.variables['longitude'][:])
    obs_hs = np.array(datanc.variables['hs'][:])
    obs_wnd = np.array(datanc.variables['wsp_cal'][:])
    model_hs = np.array(datanc.variables['swh_interpolated'][:])
    model_wnd = np.array(datanc.variables['ws_interpolated'][:])

    res_date=datetime.date(2020, 9, 13)
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')

    fhrs=np.array((validtime-refcdate)/3600)


    indx=np.where((fhrs < 24.) & (fhrs>1)) 
    model_hs1=model_hs[indx]
    obs_hs1=obs_hs[indx]
    lats1=lats[indx]
    lons1=lons[indx]
    obs_wnd1=obs_wnd[indx]
    model_wnd1=model_wnd[indx]

    indx=np.where((fhrs < 48.) & (fhrs>24))
    model_hs2=model_hs[indx]
    obs_hs2=obs_hs[indx]
    lats2=lats[indx]
    lons2=lons[indx]
    obs_wnd2=obs_wnd[indx]
    model_wnd2=model_wnd[indx]

    indx=np.where((fhrs < 72.) & (fhrs>48))
    model_hs3=model_hs[indx]
    obs_hs3=obs_hs[indx]
    lats3=lats[indx]
    lons3=lons[indx]
    obs_wnd3=obs_wnd[indx]
    model_wnd3=model_wnd[indx]

    indx=np.where((fhrs < 96.) & (fhrs>72))
    model_hs4=model_hs[indx]
    obs_hs4=obs_hs[indx]
    lats4=lats[indx]
    lons4=lons[indx]
    obs_wnd4=obs_wnd[indx]
    model_wnd4=model_wnd[indx]

    indx=np.where((fhrs < 120.) & (fhrs>96))
    model_hs5=model_hs[indx]
    obs_hs5=obs_hs[indx]
    lats5=lats[indx]
    lons5=lons[indx]
    obs_wnd5=obs_wnd[indx]
    model_wnd5=model_wnd[indx]


    indx=np.where((fhrs < 144) & (fhrs>120))
    model_hs6=model_hs[indx]
    obs_hs6=obs_hs[indx]
    lats6=lats[indx]
    lons6=lons[indx]
    obs_wnd6=obs_wnd[indx]
    model_wnd6=model_wnd[indx]

    indx=np.where((fhrs < 168.) & (fhrs>144))
    model_hs7=model_hs[indx]
    obs_hs7=obs_hs[indx]
    lats7=lats[indx]
    lons7=lons[indx]
    obs_wnd7=obs_wnd[indx]
    model_wnd7=model_wnd[indx]

    diff = model_hs1-obs_hs1 
    bias1 = diff.mean()
    rmse1 = (diff**2).mean()**0.5
    SI1   = 100.0*(((diff**2).mean())**0.5 - bias1**2)/obs_hs1.mean() #scatter_index

    diff = model_hs2-obs_hs2
    bias2 = diff.mean()
    rmse2 = (diff**2).mean()**0.5
    SI2   = 100.0*(((diff**2).mean())**0.5 - bias2**2)/obs_hs2.mean() #scatter_index

    
    diff = model_hs3-obs_hs3
    bias3 = diff.mean()
    rmse3 = (diff**2).mean()**0.5
    SI3   = 100.0*(((diff**2).mean())**0.5 - bias3**2)/obs_hs3.mean() #scatter_index

    diff = model_hs4-obs_hs4
    bias4 = diff.mean()
    rmse4 = (diff**2).mean()**0.5
    SI4   = 100.0*(((diff**2).mean())**0.5 - bias4**2)/obs_hs4.mean() #scatter_index

    diff = model_hs5-obs_hs5
    bias5 = diff.mean()
    rmse5 = (diff**2).mean()**0.5
    SI5   = 100.0*(((diff**2).mean())**0.5 - bias5**2)/obs_hs4.mean() #scatter_index

    diff = model_hs6-obs_hs6
    bias6 = diff.mean()
    rmse6 = (diff**2).mean()**0.5
    SI6   = 100.0*(((diff**2).mean())**0.5 - bias6**2)/obs_hs6.mean() #scatter_index


    diff = model_hs7-obs_hs7
    bias7 = diff.mean()
    rmse7 = (diff**2).mean()**0.5
    SI7   = 100.0*(((diff**2).mean())**0.5 - bias7**2)/obs_hs7.mean() #scatter_index


    HR3abias=[bias1,bias2,bias3,bias4,bias5,bias6,bias7]
    HF3armse=[rmse1, rmse2, rmse3, rmse4, rmse5, rmse6, rmse7]
    HR3aSI7=[SI1, SI2, SI3, SI4, SI5, SI6,SI7]

    print('HR3a')
    print('HR3abias', HR3abias) 
    print('HR3armse', HF3armse) 
    print('HR3aSI7', HR3aSI7)
    


if __name__ == '__main__':
    main()
