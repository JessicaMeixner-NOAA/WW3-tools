import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc

from emcpy.plots import CreatePlot, CreateFigure
from emcpy.plots.map_tools import Domain, MapProjection
from emcpy.plots.map_plots import MapGridded


def main():
  fhrs=[1,2,3,12,24,36,48,72,96,120,144,168]
  for fhr in fhrs:
    print('fhr=',fhr)
    basepath='/work/noaa/marine/jmeixner/Data/HR3b/hurricane/gfs.20200913/00/products/wave/gridded'
    prepath='gfswave.t00z.global.0p25.f'
    filepath=basepath+'/'+prepath+'%03d.grib2.nc' % (fhr)
    datanc  = nc.Dataset(filepath)

    validtime = np.array(datanc.variables['time'][:]).astype('double')
    lats  = np.array(datanc.variables['latitude'][:])
    lons  = np.array(datanc.variables['longitude'][:])
    hs = np.array(datanc.variables['HTSGW_surface'][:])
    fill_val_hs = datanc.variables['HTSGW_surface'].__dict__['_FillValue']
    wnd = np.array(datanc.variables['WIND_surface'][:])
    fill_val_wnd = datanc.variables['WIND_surface'].__dict__['_FillValue']

    indx=np.where(hs==fill_val_hs) 
    hs[indx]=np.nan 
    indx=np.where(wnd==fill_val_wnd) 
    wnd[indx]=np.nan

    X, Y = np.meshgrid(lats, lons)


    # Create gridded map object
    gridded = MapGridded(X, Y, np.transpose( hs[0] ))
    gridded.cmap = 'turbo'
    gridded.vmin = 0
    gridded.vmax = 15 

    # Create plot object and add features
    plot1 = CreatePlot()
    plot1.plot_layers = [gridded]
    plot1.projection = 'plcarr'
    plot1.domain = 'global'
    plot1.add_map_features(['coastline'])
    plot1.add_xlabel(xlabel='longitude')
    plot1.add_ylabel(ylabel='latitude')
    titleofplot='HR3b IC 2020091300 fhr %03d' % fhr 
    plot1.add_title(label=titleofplot, loc='center')
    plot1.add_grid()
    plot1.add_colorbar(label='Significant Wave Height [m]',
                       fontsize=12, extend='neither')

    # Create figure
    fig = CreateFigure()
    fig.plot_list = [plot1]
    fig.create_figure()
    
    figname='hsglobalHR3b.f%03d.png' % (fhr)
    fig.save_figure(figname ) 
    fig.close_figure()


    atlantic_dict = {
        "extent": (-100, -20, 10, 70),
        "xticks": (-90, -80, -70, -60, -50, -40, -30),
        "yticks": (20, 30, 40, 50, 60),
        "cenlon": -60.,
        "cenlat": 40.
     }

    plot2 = CreatePlot() 
    plot2.plot_layers = [gridded]
    plot2.projection = 'plcarr'

    plot2.domain = ('custom', atlantic_dict)
    plot2.add_map_features(['coastline'])
    plot2.add_xlabel(xlabel='longitude')
    plot2.add_ylabel(ylabel='latitude')
    titleofplot='HR3b IC 2020091300 fhr %03d' % fhr
    plot2.add_title(label=titleofplot, loc='center')
    plot2.add_grid()
    plot2.add_colorbar(label='Significant Wave Height [m]',
                       fontsize=12, extend='neither')

    # Create figure
    fig = CreateFigure()
    fig.plot_list = [plot2]
    fig.create_figure()

    figname='hsatlanticHR3b.f%03d.png' % (fhr)
    fig.save_figure(figname )
    fig.close_figure()




if __name__ == '__main__':
    main()
