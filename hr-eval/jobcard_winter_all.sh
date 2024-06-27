#!/bin/sh
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00  # Adjust this time as needed for the job submission process
#SBATCH --partition=hera
#SBATCH --account=marine-cpu
#SBATCH --job-name=submit_jobs
#SBATCH --output=submit_jobs_logfile-%j.out

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 start_date end_date"
    echo "Dates should be in the format YYYYMMDDHH"
    exit 1
fi

# Define variables
start_date=$1
end_date=$2

base_path="/scratch2/NCEPDEV/marine/Jessica.Meixner/Data/multi1"
buoy_path="/scratch2/NCEPDEV/marine/Matthew.Masarik/dat/buoys/NDBC/ncformat/wparam"
model_name="multi1-winter"  # Define the model name
forecast_ds="1"    # Indicator for forecast data structure, set to 1 or 0 based on requirements

# Convert start and end dates to seconds since epoch for easier manipulation
start_date_sec=$(date -d "${start_date:0:8}" +%s)
end_date_sec=$(date -d "${end_date:0:8}" +%s)
start_hour=${start_date:8:2}

# Loop through each date from start date to end date
for current_date_sec in $(seq $start_date_sec 86400 $end_date_sec); do
    current_date=$(date -d "@$current_date_sec" +%Y%m%d)
    current_datetime="${current_date}${start_hour}"
    job_name="process_data_${current_datetime}"

    # Define the output directory for the current date
    output_directory="/scratch2/NCEPDEV/marine/Ghazal.Mohammadpour/Tools/Buoyval-multi1/Buoy_branch/WW3-tools/ww3tools/${current_datetime}"

    # Create the job script for the current date
    cat <<EOT > job_${current_datetime}.sh
#!/bin/sh --login
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=08:00:00
#SBATCH --partition=hera
#SBATCH --account=marine-cpu
#SBATCH --job-name=$job_name
#SBATCH --output=logfile-winter-%j.out

# Load necessary modules
module use /scratch1/NCEPDEV/climate/Jessica.Meixner/general/modulefiles-rocky16
module load ww3tools

# Define variables
base_path="$base_path"
buoy_path="$buoy_path"
model_name="$model_name"
forecast_ds="$forecast_ds"
current_datetime="$current_datetime"
output_directory="$output_directory"

# Create the output directory if it doesn't exist
mkdir -p "\$output_directory"

date_dir="\$base_path/\$current_datetime"
input_gz_file="\$date_dir/multi_1.t00z.spec_tar.gz"

# Check if the input file exists
if [ -f "\$input_gz_file" ]; then
    # Process data for the current date
    python3 modelBuoy_collocation.py spec.gz "\$input_gz_file" "\$output_directory" "$buoy_path" "$model_name" "$forecast_ds"
else
    echo "File \$input_gz_file does not exist for date \$current_datetime."
fi
EOT

    # Submit the job
    sbatch job_${current_datetime}.sh
done

