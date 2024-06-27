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

# Define variables
input_gz_file="xxx/gfswave.t00z.spec_tar.gz"
output_directory="./"
buoy_path="/scratch2/NCEPDEV/marine/Matthew.Masarik/dat/buoys/NDBC/ncformat/wparam"
model_name="HR2"  # Define the model name
forecast_ds="1"    # Indicator for forecast data structure, set to 1 or 0 based on requirements
# Process data for each date
python3 modelBuoy_collocation.py spec.gz "$input_gz_file" "$output_directory" "$buoy_path" "$model_name" "$forecast_ds"

