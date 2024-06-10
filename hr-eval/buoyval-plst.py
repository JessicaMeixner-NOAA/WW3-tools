import os
import json
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pvalstats import ModelObsPlot
import mvalstats

# Load configuration from JSON file
with open('configuration.json', 'r') as f:
    config = json.load(f)

process_buoys_separately = config['process_buoys_separately']
directory_path = config['directory_path']
forecast_ranges = [tuple(range_pair) for range_pair in config['forecast_ranges']]

# Process each forecast range separately
for start, end in forecast_ranges:
    range_label = f"{start}to{end}hrs"
    all_buoys_data = {'time': [], 'model_hs': [], 'obs_hs': []}

    # Process each netCDF file in the directory
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.nc'):
            file_path = os.path.join(directory_path, file_name)

            # Load the netCDF file
            data = xr.open_dataset(file_path)

            # Check available variables
            available_vars = list(data.variables.keys())
            print(f"Processing {file_name}, available variables: {available_vars}")

            # Skip files that do not contain 'fcst_hr'
            if 'fcst_hr' not in data.variables:
                print(f"Skipping {file_name} as it does not contain 'fcst_hr'")
                continue

            # Find buoy IDs variable name
            buoy_id_var_name = None
            for var in available_vars:
                if 'buoy' in var.lower() and 'id' in var.lower():
                    buoy_id_var_name = var
                    break

            if not buoy_id_var_name:
                print(f"No buoy ID variable found in {file_name}")
                continue

            # Extract relevant variables
            buoy_ids = data[buoy_id_var_name].values
            init_time = data['time'].values[0]  # Assuming a single initialization time
            fcst_hr = data['fcst_hr'].values
            model_hs = data['model_hs'].values
            obs_hs = data['obs_hs'].values

            # Convert initialization time from seconds since epoch to datetime
            init_time_dt = pd.to_datetime(init_time, unit='s')

            # Convert forecast hours to numeric hours
            fcst_hr_numeric = fcst_hr.astype('timedelta64[h]').astype(int)

            # Process data for each buoy and forecast range
            for i, buoy_id in enumerate(buoy_ids):
                # Generate full timestamps for each forecast lead time
                full_timestamps = init_time_dt + pd.to_timedelta(fcst_hr_numeric[i, :], unit='h')

                # Mask for the current forecast range
                forecast_mask = (fcst_hr_numeric[i, :] >= start) & (fcst_hr_numeric[i, :] < end)

                # Print the shapes of the masks and indices for debugging
                print(f"Processing buoy {buoy_id} for range {start}-{end} hours")
                print(f"Shape of forecast_mask: {forecast_mask.shape}")

                filtered_time_dt = full_timestamps[forecast_mask]
                filtered_model_hs = model_hs[i, 0, forecast_mask]
                filtered_obs_hs = obs_hs[i, 0, forecast_mask]

                # Print the shapes of the filtered data for debugging
                print(f"Shape of filtered_time_dt: {filtered_time_dt.shape}")
                print(f"Shape of filtered_model_hs: {filtered_model_hs.shape}")
                print(f"Shape of filtered_obs_hs: {filtered_obs_hs.shape}")

                if filtered_time_dt.size > 0:
                    all_buoys_data['time'].append(filtered_time_dt)
                    all_buoys_data['model_hs'].append(filtered_model_hs)
                    all_buoys_data['obs_hs'].append(filtered_obs_hs)

    # Concatenate the combined data for all buoys
    combined_time = np.concatenate(all_buoys_data['time'])
    combined_model_hs = np.concatenate(all_buoys_data['model_hs'])
    combined_obs_hs = np.concatenate(all_buoys_data['obs_hs'])

    # Create an xarray Dataset for the combined data
    combined_data = xr.Dataset({
        'time': ('time', combined_time),
        'model_hs': ('time', combined_model_hs),
        'obs_hs': ('time', combined_obs_hs)
    })

    # Create a subdirectory for the current range
    range_dir = os.path.join(directory_path, range_label)
    os.makedirs(range_dir, exist_ok=True)

    # Plot the combined data time series
    plt.figure(figsize=(12, 8))
    plt.scatter(combined_data['time'], combined_data['model_hs'], label='Model HS', marker='o')
    plt.scatter(combined_data['time'], combined_data['obs_hs'], label='Observed HS', marker='x')
    plt.xlabel('Time')
    plt.ylabel('Significant Wave Height (m)')
    plt.title(f'Significant Wave Height Comparison for All Buoys ({range_label})')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the time series plot
    plot_path = os.path.join(range_dir, f'all_buoys_combined_{range_label}_plot.png')
    plt.savefig(plot_path)
    plt.close()
    print(f"Time series plot saved as {plot_path}")

    # Calculate statistics
    smr_stats_model = mvalstats.smrstat(combined_model_hs)
    smr_stats_obs = mvalstats.smrstat(combined_obs_hs)
    metrics_stats = mvalstats.metrics(combined_model_hs, combined_obs_hs)

    # Create dataframes for statistics
    stats_df = pd.DataFrame({
        'Metric': ['Mean', 'Variance', 'Skewness', 'Kurtosis', 'Min', 'Max', 'Percentile80', 'Percentile90', 'Percentile95', 'Percentile99', 'Percentile99.9'],
        'Model': smr_stats_model,
        'Observation': smr_stats_obs
    })

    metrics_df = pd.DataFrame({
        'Metric': ['Bias', 'RMSE', 'Normalized Bias', 'Normalized RMSE', 'Scatter Component of RMSE', 'Scatter Index', 'HH', 'Correlation Coefficient', 'Number of Observations'],
        'Value': metrics_stats
    })

    # Save statistics to an Excel file
    stats_file = os.path.join(range_dir, f'all_buoys_combined_{range_label}_statistics.xlsx')
    with pd.ExcelWriter(stats_file, engine='xlsxwriter') as writer:
        stats_df.to_excel(writer, sheet_name='Stats', index=False)
        metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
    print(f"Statistics saved to {stats_file}")

    # Prepare data for Taylor diagram and scatter plot
    model_data = combined_model_hs.reshape(1, -1)
    obs_data = combined_obs_hs.reshape(1, -1)
    mlabels = ['Model HS']
    ftag = os.path.join(range_dir, f'all_buoys_combined_{range_label}_')

    # Taylor Diagram
    mop = ModelObsPlot(model=model_data, obs=obs_data, mlabels=mlabels, axisnames=["Observed HS", "Model HS"], ftag=ftag)
    mop.taylordiagram()

    # Scatter Plot
    mop.scatterplot()

# Process each buoy separately if the switch is set to True
if process_buoys_separately:
    # Dictionary to store combined data for each buoy and forecast range
    buoy_data = {}

    # Process each netCDF file in the directory
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.nc'):
            file_path = os.path.join(directory_path, file_name)

            # Load the netCDF file
            data = xr.open_dataset(file_path)

            # Check available variables
            available_vars = list(data.variables.keys())
            print(f"Processing {file_name}, available variables: {available_vars}")

            # Find buoy IDs variable name
            buoy_id_var_name = None
            for var in available_vars:
                if 'buoy' in var.lower() and 'id' in var.lower():
                    buoy_id_var_name = var
                    break

            if not buoy_id_var_name:
                print(f"No buoy ID variable found in {file_name}")
                continue

            # Extract relevant variables
            buoy_ids = data[buoy_id_var_name].values
            time = data['time'].values[0, :]  # assuming fcycle is always 0
            fcst_hr = data['fcst_hr'].values
            model_hs = data['model_hs'].values[:, 0, :]
            obs_hs = data['obs_hs'].values[:, 0, :]

            # Convert time from seconds since epoch to datetime
            time_dt = pd.to_datetime(time, unit='s')

            # Convert forecast hours to numeric hours
            fcst_hr_numeric = fcst_hr.astype('timedelta64[h]').astype(int)

            # Process data for each buoy
            for i, buoy_id in enumerate(buoy_ids):
                for start, end in forecast_ranges:
                    # Mask for the specified forecast range
                    range_mask = (fcst_hr_numeric >= start) & (fcst_hr_numeric < end)

                    filtered_time_dt = time_dt[range_mask[i, :]]
                    filtered_model_hs = model_hs[i, range_mask[i, :]]
                    filtered_obs_hs = obs_hs[i, range_mask[i, :]]

                    if filtered_time_dt.size > 0:
                        range_key = f'{start}_{end}hrs'
                        if buoy_id not in buoy_data:
                            buoy_data[buoy_id] = {}

                        if range_key not in buoy_data[buoy_id]:
                            buoy_data[buoy_id][range_key] = {'time': [], 'model_hs': [], 'obs_hs': []}

                        buoy_data[buoy_id][range_key]['time'].append(filtered_time_dt)
                        buoy_data[buoy_id][range_key]['model_hs'].append(filtered_model_hs)
                        buoy_data[buoy_id][range_key]['obs_hs'].append(filtered_obs_hs)

    # Save and analyze data for each buoy and forecast range
    for buoy_id, ranges_data in buoy_data.items():
        for range_key, data in ranges_data.items():
            # Concatenate the combined data
            combined_time = np.concatenate(data['time'])
            combined_model_hs = np.concatenate(data['model_hs'])
            combined_obs_hs = np.concatenate(data['obs_hs'])

            # Create an xarray Dataset
            combined_data = xr.Dataset({
                'time': ('time', combined_time),
                'model_hs': ('time', combined_model_hs),
                'obs_hs': ('time', combined_obs_hs)
            })

            # Plot the combined data
            plt.figure(figsize=(12, 8))
            plt.scatter(combined_data['time'], combined_data['model_hs'], label=f'Model HS - Buoy {buoy_id}', marker='o')
            plt.scatter(combined_data['time'], combined_data['obs_hs'], label=f'Observed HS - Buoy {buoy_id}', marker='x')
            plt.xlabel('Time')
            plt.ylabel('Significant Wave Height (m)')
            plt.title(f'Significant Wave Height Comparison for Buoy {buoy_id} ({range_key} from All Files)')
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Save the plot
            plot_path = os.path.join(directory_path, f'{buoy_id}_combined_{range_key}_plot.png')
            plt.savefig(plot_path)
            plt.close()
            print(f"Plot saved as {plot_path}")

            # Calculate statistics
            smr_stats_model = mvalstats.smrstat(combined_model_hs)
            smr_stats_obs = mvalstats.smrstat(combined_obs_hs)
            metrics_stats = mvalstats.metrics(combined_model_hs, combined_obs_hs)

            # Create dataframes for statistics
            stats_df = pd.DataFrame({
                'Metric': ['Mean', 'Variance', 'Skewness', 'Kurtosis', 'Min', 'Max', 'Percentile80', 'Percentile90', 'Percentile95', 'Percentile99', 'Percentile99.9'],
                'Model': smr_stats_model,
                'Observation': smr_stats_obs
            })

            metrics_df = pd.DataFrame({
                'Metric': ['Bias', 'RMSE', 'Normalized Bias', 'Normalized RMSE', 'Scatter Component of RMSE', 'Scatter Index', 'HH', 'Correlation Coefficient', 'Number of Observations'],
                'Value': metrics_stats
            })

            # Save statistics to an Excel file
            stats_file = os.path.join(directory_path, f'{buoy_id}_combined_{range_key}_statistics.xlsx')
            with pd.ExcelWriter(stats_file, engine='xlsxwriter') as writer:
                stats_df.to_excel(writer, sheet_name='Stats', index=False)
                metrics_df.to_excel(writer, sheet_name='Metrics', index=False)
            print(f"Statistics saved to {stats_file}")

            # Prepare data for Taylor diagram and scatter plot
            model_data = combined_model_hs.reshape(1, -1)
            obs_data = combined_obs_hs.reshape(1, -1)
            mlabels = [f'Model HS - Buoy {buoy_id}']
            ftag = os.path.join(directory_path, f'{buoy_id}_combined_{range_key}_')

            # Taylor Diagram
            mop = ModelObsPlot(model=model_data, obs=obs_data, mlabels=mlabels, axisnames=["Observed HS", "Model HS"], ftag=ftag)
            mop.taylordiagram()

            # Scatter Plot
            mop.scatterplot()

