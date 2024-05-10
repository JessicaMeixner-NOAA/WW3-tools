# HR Evaluation Steps 

## Process Sat info 

## Interpolate model to statelite track 

## Combine output of interpolated model to satelite track 

The previous step is completed for each forecast hour and for multi-grid scenarios, each grid.  This step combines the output 
by season for each model for each satelite, taking into account multi-grids for Multi1 and GFSv16.  For each model the following
is run: 

``` python CombineSatInterpOut.py -m $MODEL -o $OUTDIR ```

where MODEL=multi1, GFSv16, HR1, HR2, HR3a, HR3b and OUTDIR is the desired output directory. 

The output is a series of files 
`combined_${MODEL}_${SEASON}_${SATELITE}.nc`
for the combined output and then `combined_day${DAY}_${MODEL}_${SEASON}_${SATELITE}.nc` for the model output for each day. 

To check this, we need to make sure that we have all of the expected files exist and that they all are of non-zero size, 
in addition to checking that there were not errors in the log files from the jobs. 
Note, the size of the mutli1 files are smaller because it does not have the same length of forecast and the hurricane 
output for GFSv16 is lareger than HR runs as it goes out to 16, not 7 days. 

The number of expected output files is: 

| Number of Files | Model | Calculation | 
|:------------------:|:-----------------:|:----------------------:|
| 96 |  multi1  | ( (7 days + 1 combined) x ( 3 seasons ) x (4 satelites) ) | 
|  100 |  GFSv16  | ( (7 days + 1 combined) x (1 hurricane season) x (4 satelites) + (16 days + 1 combined) x (1 summer season) x (4 satelites) ) |
|  168 |  HR experiements |  ( (7 days + 1 combined) x (1 hurricane season) x (4 satelites) + (16 days + 1 combined) x (2 summer/winter season) x (4 satelites )) |

This steps output can be found: 

| Machine | Directory Location | 
|:------------------:|:-----------------:|
| hera | /scratch1/NCEPDEV/climate/Jessica.Meixner/processsatdata/combineout|
| orion |  /work2/noaa/marine/jmeixner/processsatdata/combineout |


## Scripts used to create the plots: 

1- first of all I tried to get the .nc files for example day1, day2, ... , day7. The reason that I chose to save the 
.nc files is that for me it was easier to do the statistcs using the .nc output. (You may have other ideas)  
(code is time-f.py)
(we have satellite interpolated outputs. In order to get the first day of different initial conditions, I used time-f.py 
to get the specific day)
You can do that automatically for different models using the config.json file.

* An alternative script to obtain combined NetCDF files that is specific to the HR evaluations is CombineSatInterpOut.py 
This script combines files by day, adds high resolution grid information for mutli1 and GFSv16.  It also adds NaNs to the
model wind values where the grib file had zeros at f000.  The limitation of this routine is that it is not generic and 
has hard-coded expectations of the file names.  It should work without modification on both hera or orion.   

2- Then I used the eval.py to plot them. for plotting them you need to call pvalstats.py. The script is (eval.py). This is an automated process. In order to run the code you have to define the evalsumconfig.json. In this file you have to define the directory , filename, satellite name and then you can run the code.It accepts multiple pathes and filenames.

3- for the statistcal analysis I used the code and called mvalstats.py to calculate the statistcs. (stat.py)It created the spreadsheets with this format ({folder}_stats.csv)

4- plotstat.py, in this code you can plot the outputs of the stat.py. In the code, there is a switch that you can define if you want to consider all the vlues for all the models or the amount that covers all of them. when this value ()
is False,it plots the full range and when it is true it only plots up to values that is covered by all of the inputs. 
