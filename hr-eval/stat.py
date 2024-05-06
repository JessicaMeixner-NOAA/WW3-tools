import os
import pandas as pd
import netCDF4 as nc
import mvalstats

# Define the base directory where the folders are located
base_dir = '/scratch2/NCEPDEV/marine/Ghazal.Mohammadpour/transfer/validation/WW3-tools/ww3tools/ORION/WW3-tools/ww3tools/output/HR3a'

# List of folders to process
folders = [ 'hurricane']

# Statistics and summary results will be stored in a dictionary
results = {}

# Iterate over each folder
for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    files = os.listdir(folder_path)
    # Prepare a list to collect DataFrames for each file in this folder
    all_file_stats = []
    
    # Iterate over each file in the current folder
    for file in files:
        if file.endswith('.nc'):
            file_path = os.path.join(folder_path, file)
            # Open the .nc file
            nc_file = nc.Dataset(file_path, 'r')
            
            # Load model and observation data for wave height and wind
            model_hs_data = nc_file.variables['model_hs'][:]
            obs_hs_data = nc_file.variables['obs_hs'][:]
            model_wnd_data = nc_file.variables['model_wnd'][:]
            obs_wnd_data = nc_file.variables['obs_wnd'][:]
            
            # Close the .nc file
            nc_file.close()
            
            # Call metrics function for wave height
            rmse_hs_result = mvalstats.metrics(model_hs_data, obs_hs_data)
            # Call metrics function for wind
            rmse_wnd_result = mvalstats.metrics(model_wnd_data, obs_wnd_data)
            
            # Collect all results into a DataFrame
            file_stats = pd.DataFrame({
                'File': [file],
                'HS Bias': [rmse_hs_result[0]],
                'HS RMSE': [rmse_hs_result[1]],
                'HS Normalized Bias': [rmse_hs_result[2]],
                'HS Normalized RMSE': [rmse_hs_result[3]],
                'HS SCrmse': [rmse_hs_result[4]],
                'HS SI': [rmse_hs_result[5]],
                'HS HH': [rmse_hs_result[6]],
                'HS CC': [rmse_hs_result[7]],
                'WND Bias': [rmse_wnd_result[0]],
                'WND RMSE': [rmse_wnd_result[1]],
                'WND Normalized Bias': [rmse_wnd_result[2]],
                'WND Normalized RMSE': [rmse_wnd_result[3]],
                'WND SCrmse': [rmse_wnd_result[4]],
                'WND SI': [rmse_wnd_result[5]],
                'WND HH': [rmse_wnd_result[6]],
                'WND CC': [rmse_wnd_result[7]]
            })
            
            # Append the statistics DataFrame to the list
            all_file_stats.append(file_stats)
    
    # Concatenate all DataFrames in the list to form the final DataFrame for this folder
    stats_df = pd.concat(all_file_stats, ignore_index=True)
    
    # Store the DataFrame for this folder in the results dictionary
    results[folder] = stats_df

# Now, you can access the results for each folder and print or save them
for folder, df in results.items():
    print(f"Statistics for {folder}:")
    print(df)
    # Optionally, save the DataFrame to a CSV file
    df.to_csv(f'{folder}_stats.csv', index=False)
