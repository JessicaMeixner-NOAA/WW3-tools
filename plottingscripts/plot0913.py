import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapScatter


def main():
    # Create test data
    datapath='/work/noaa/marine/jmeixner/2020091300/HR3ascout_JASON3_2020091300.nc'
    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    latsHR3  = np.array(datanc.variables['latitude'][:])
    lonsHR3  = np.array(datanc.variables['longitude'][:])
    obs_hsHR3 = np.array(datanc.variables['hs'][:])
    obs_wndHR3 = np.array(datanc.variables['wsp_cal'][:])
    model_hsHR3 = np.array(datanc.variables['swh_interpolated'][:])
    model_wndHR3 = np.array(datanc.variables['ws_interpolated'][:])
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')
    fhrsHR3=np.array((validtime-refcdate)/3600)


    datapath='/work/noaa/marine/jmeixner/2020091300/HR1hurr_JASON3_2020091300.nc'
    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    latsHR1  = np.array(datanc.variables['latitude'][:])
    lonsHR1  = np.array(datanc.variables['longitude'][:])
    obs_hsHR1 = np.array(datanc.variables['hs'][:])
    obs_wndHR1 = np.array(datanc.variables['wsp_cal'][:])
    model_hsHR1 = np.array(datanc.variables['swh_interpolated'][:])
    model_wndHR1 = np.array(datanc.variables['ws_interpolated'][:])
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')
    fhrsHR1=np.array((validtime-refcdate)/3600)


    datapath='/work/noaa/marine/jmeixner/2020091300/HR2hurr_JASON3_2020091300.nc'
    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    latsHR2  = np.array(datanc.variables['latitude'][:])
    lonsHR2  = np.array(datanc.variables['longitude'][:])
    obs_hsHR2 = np.array(datanc.variables['hs'][:])
    obs_wndHR2 = np.array(datanc.variables['wsp_cal'][:])
    model_hsHR2 = np.array(datanc.variables['swh_interpolated'][:])
    model_wndHR2 = np.array(datanc.variables['ws_interpolated'][:])
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')
    fhrsHR2=np.array((validtime-refcdate)/3600)


    datapath='/work/noaa/marine/jmeixner/2020091300/GFSv16hurr_JASON3_2020091300.nc'
    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    latsGFS  = np.array(datanc.variables['latitude'][:])
    lonsGFS  = np.array(datanc.variables['longitude'][:])
    obs_hsGFS = np.array(datanc.variables['hs'][:])
    obs_wndGFS = np.array(datanc.variables['wsp_cal'][:])
    model_hsGFS = np.array(datanc.variables['swh_interpolated'][:])
    model_wndGFS = np.array(datanc.variables['ws_interpolated'][:])
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')
    fhrsGFS=np.array((validtime-refcdate)/3600)

    datapath='/work/noaa/marine/jmeixner/2020091300/multi1hurr_JASON3_2020091300.nc'
    datanc  = nc.Dataset(datapath)
    validtime = np.array(datanc.variables['time'][:])
    latsM1  = np.array(datanc.variables['latitude'][:])
    lonsM1  = np.array(datanc.variables['longitude'][:])
    obs_hsM1 = np.array(datanc.variables['hs'][:])
    obs_wndM1 = np.array(datanc.variables['wsp_cal'][:])
    model_hsM1 = np.array(datanc.variables['swh_interpolated'][:])
    model_wndM1 = np.array(datanc.variables['ws_interpolated'][:])
    refcdate=((np.datetime64(res_date) - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's')).astype('double')
    fhrsM1=np.array((validtime-refcdate)/3600)


    # Create scatter plot on CONUS domian
    scatter = MapScatter(lats, lons, obs_hs-model_hs)
    # change colormap and markersize
    scatter.cmap = 'bwr'
    scatter.markersize = 25
    scatter.vmin=-5
    scatter.vmax=5

    # Create plot object and add features
    plot1 = CreatePlot()
    plot1.plot_layers = [scatter]
    plot1.projection = 'plcarr'
    plot1.domain = 'global'
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    plot1.add_title(label='HS', loc='center',
                    fontsize=20)
    plot1.add_colorbar(label='colorbar label',
                       fontsize=12, extend='neither')

    # annotate some stats
    #stats_dict = {
    #    'nobs': len(np.linspace(200, 300, 30)),
    #    'vmin': 200,
    #    'vmax': 300,
    #}
    #plot1.add_stats_dict(stats_dict=stats_dict, yloc=-0.175)

    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()

    #plotpath = outpath+'/scatter'+'%03d.png' % (ihr)
    fig.save_figure('hsdiff_hr3aJASON3alltime.png')
    fig.close_figure()    



if __name__ == '__main__':
    main()
