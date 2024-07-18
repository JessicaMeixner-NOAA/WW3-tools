import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import argparse

import datetime as dt
from dateutil.relativedelta import relativedelta
import os

import mvalstats



'''
Read stats and plot 
'''

def main():


  datapath = "/scratch1/NCEPDEV/climate/Jessica.Meixner/uifcwhreval/WW3-tools/hr-eval/statshr3.nc"

  datanc  = nc.Dataset(datapath)

  allstats_hs = np.array(datanc.variables['allstats_hs'][:])
  allstats_wnd = np.array(datanc.variables['allstats_wnd'][:])
  allstats_hs_cal = np.array(datanc.variables['allstats_hs_cal'][:])
  allstats_wnd_cal = np.array(datanc.variables['allstats_wnd_cal'][:])

  #allstats_wnd  _cal
  datanc.close()




if __name__ == '__main__':
    main()

