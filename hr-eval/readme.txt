Scripts used to create the plots: 

1- first of all I tried to get the .nc files for example day1, day2, ... , day7. The reason that I chose to save the 
.nc files is that for me it was easier to do the statistcs using the .nc output. (You may have other ideas)  
(code is time-f.py)
(we have satellite interpolated outputs. In order to get the first day of different initial conditions, I used time-f.py 
to get the specific day)
You can do that automatically for different models using the config.json file.

2- Then I used the eval.py to plot them. for plotting them you need to call pvalstats.py. The script is (eval.py). This is an automated process. In order to run the code you have to define the evalsumconfig.json. In this file you have to define the directory , filename, satellite name and then you can run the code.It accepts multiple pathes and filenames.

3- for the statistcal analysis I used the code and called mvalstats.py to calculate the statistcs. (stat.py)It created the spreadsheets with this format ({folder}_stats.csv)

4- plotstat.py, in this code you can plot the outputs of the stat.py. In the code, there is a switch that you can define if you want to consider all the vlues for all the models or the amount that covers all of them. when this value ()
is False,it plots the full range and when it is true it only plots up to values that is covered by all of the inputs. 
