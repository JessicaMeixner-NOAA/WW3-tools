#!/bin/sh --login
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:30:00
#SBATCH --partition=hera
#SBATCH --account=marine-cpu
#SBATCH --job-name=process_data
#SBATCH --output=logfile.out
#SBATCH -q debug

# Load necessary modules
module use /scratch1/NCEPDEV/climate/Jessica.Meixner/general/modulefiles-rocky16
module load ww3tools

buoy_path="/scratch2/NCEPDEV/marine/Matthew.Masarik/dat/buoys/NDBC/ncformat/wparam"


# Process data for each date
python3 modelBuoy_collocation.py ww3list.txt 2 $buoy_path gridInfo_GEFS.nc CycloneMap_2018.nc
  



#(gridInfo_GEFS.nc CycloneMap_2018.nc is optional. User can remove it. When user remove these two optional items, it will look like: python3 modelBuoy_collocation.py ww3list.txt 2 $buoy_path )
