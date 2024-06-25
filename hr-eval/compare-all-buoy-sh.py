import os
import json
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pvalstats import ModelObsPlot
import mvalstats

# Load configuration from JSON file, any file name can be used
with open('configuration3.json', 'r') as f:
    config = json.load(f)

process_buoys_separately = config['process_buoys_separately']
model_paths = {k: v for k, v in config['models'].items() if k in ['hr3a', 'hr3b']}
forecast_ranges = [tuple(range_pair) for range_pair in config['forecast_ranges']]
plot_combined_taylor = config.get('plot_combined_taylor', False)
directory_path = config['directory_path']

def get_common_buoy_ids(model_paths):
    buoy_id_sets = []
    for model_name, model_dir in model_paths.items():
        for file_name in os.listdir(model_dir):
            if file_name.endswith('.nc'):
                file_path = os.path.join(model_dir, file_name)
                data = xr.open_dataset(file_path)
                if 'buoyID' in data.variables:
                    buoy_ids = set(data['buoyID'].values)
                    buoy_id_sets.append(buoy_ids)
                    break  # Only need to process one file per model to get the buoy IDs

    if buoy_id_sets:
        common_buoy_ids = set.intersection(*buoy_id_sets)
        return common_buoy_ids
    else:
        return set()

def process_model_data(model_name, model_dir, start, end, common_buoy_ids):
    range_label = f"{start}to{end}hrs"
    all_buoys_data = {'time_hs': [], 'model_hs': [], 'obs_hs': [], 'time_wind': [], 'model_wind': [], 'obs_wind': []}

    for file_name in os.listdir(model_dir):
        if file_name.endswith('.nc'):
            file_path = os.path.join(model_dir, file_name)
            data = xr.open_dataset(file_path)

            available_vars = list(data.variables.keys())
            print(f"Processing {file_name}, available variables: {available_vars}")

            if 'fcst_hr' not in data.variables or 'buoyID' not in data.variables:
                print(f"Skipping {file_name} as it does not contain 'fcst_hr' or 'buoyID'")
                continue

            buoy_ids = data['buoyID'].values
            print(f"buoy_ids for {file_name}: {buoy_ids}")

            init_time = data['time'].values[0]
            fcst_hr = data['fcst_hr'].values
            model_hs = data['model_hs'].values
            obs_hs = data['obs_hs'].values
            model_wind = data['model_wind'].values
            obs_wind = data['obs_wind'].values

            init_time_dt = pd.to_datetime(init_time, unit='s')
            fcst_hr_numeric = fcst_hr.astype('timedelta64[h]').astype(int)

            for i, buoy_id in enumerate(buoy_ids):
                if buoy_id not in common_buoy_ids:
                    continue

                full_timestamps = init_time_dt + pd.to_timedelta(fcst_hr_numeric[i, :], unit='h')
                forecast_mask = (fcst_hr_numeric[i, :] >= start) & (fcst_hr_numeric[i, :] < end)

                filtered_time_dt = full_timestamps[forecast_mask]
                filtered_model_hs = model_hs[i, 0, forecast_mask]
                filtered_obs_hs = obs_hs[i, 0, forecast_mask]
                filtered_model_wind = model_wind[i, 0, forecast_mask]
                filtered_obs_wind = obs_wind[i, 0, forecast_mask]

                if filtered_time_dt.size > 0:
                    all_buoys_data['time_hs'].append(filtered_time_dt)
                    all_buoys_data['model_hs'].append(filtered_model_hs)
                    all_buoys_data['obs_hs'].append(filtered_obs_hs)
                    all_buoys_data['time_wind'].append(filtered_time_dt)
                    all_buoys_data['model_wind'].append(filtered_model_wind)
                    all_buoys_data['obs_wind'].append(filtered_obs_wind)

    if len(all_buoys_data['model_hs']) == 0 or len(all_buoys_data['obs_hs']) == 0:
        print(f"No valid data for {model_name} {range_label}")
        return None

    combined_time_hs = np.concatenate(all_buoys_data['time_hs'])
    combined_model_hs = np.concatenate(all_buoys_data['model_hs'])
    combined_obs_hs = np.concatenate(all_buoys_data['obs_hs'])
    combined_time_wind = np.concatenate(all_buoys_data['time_wind'])
    combined_model_wind = np.concatenate(all_buoys_data['model_wind'])
    combined_obs_wind = np.concatenate(all_buoys_data['obs_wind'])

    # Remove NaN values in observation data and corresponding values in model data
    valid_mask_hs = ~np.isnan(combined_obs_hs)
    combined_time_hs = combined_time_hs[valid_mask_hs]
    combined_model_hs = combined_model_hs[valid_mask_hs]
    combined_obs_hs = combined_obs_hs[valid_mask_hs]

    valid_mask_wind = ~np.isnan(combined_obs_wind)
    combined_time_wind = combined_time_wind[valid_mask_wind]
    combined_model_wind = combined_model_wind[valid_mask_wind]
    combined_obs_wind = combined_obs_wind[valid_mask_wind]

    # Ensure model and observation data are still of the same size
    assert len(combined_model_hs) == len(combined_obs_hs), "Model and observation HS data sizes do not match after NaN removal"
    assert len(combined_model_wind) == len(combined_obs_wind), "Model and observation wind data sizes do not match after NaN removal"

    # Print the number of model points and observations
    print(f"After removing NaNs - Number of model HS points for {model_name}: {len(combined_model_hs)}")
    print(f"After removing NaNs - Number of observation HS points for {model_name}: {len(combined_obs_hs)}")
    print(f"After removing NaNs - Number of model wind points for {model_name}: {len(combined_model_wind)}")
    print(f"After removing NaNs - Number of observation wind points for {model_name}: {len(combined_obs_wind)}")

    # Print a few data points for debugging
    print(f"Sample data for {model_name} {range_label}:")
    print(f"Model HS: {combined_model_hs[:5]}")
    print(f"Observed HS: {combined_obs_hs[:5]}")
    print(f"Model Wind: {combined_model_wind[:5]}")
    print(f"Observed Wind: {combined_obs_wind[:5]}")

    # Print individual correlation coefficients for HS
    cc_individual_hs = np.corrcoef(combined_model_hs, combined_obs_hs)[0, 1]
    print(f"Individual HS CC for {model_name} {range_label}: {cc_individual_hs}")

    # Print individual correlation coefficients for Wind
    cc_individual_wind = np.corrcoef(combined_model_wind, combined_obs_wind)[0, 1]
    print(f"Individual Wind CC for {model_name} {range_label}: {cc_individual_wind}")

    # Create the combined dataset with separate time dimensions for HS and Wind
    combined_data = xr.Dataset({
        'time_hs': ('time_hs', combined_time_hs),
        'model_hs': ('time_hs', combined_model_hs),
        'obs_hs': ('time_hs', combined_obs_hs),
        'time_wind': ('time_wind', combined_time_wind),
        'model_wind': ('time_wind', combined_model_wind),
        'obs_wind': ('time_wind', combined_obs_wind)
    })

    range_dir = os.path.join(model_dir, range_label)
    os.makedirs(range_dir, exist_ok=True)

    plt.figure(figsize=(12, 8))
    plt.scatter(combined_data['time_hs'], combined_data['model_hs'], label='Model HS', marker='o')
    plt.scatter(combined_data['time_hs'], combined_data['obs_hs'], label='Observed HS', marker='x')
    plt.xlabel('Time')
    plt.ylabel('Significant Wave Height (m)')
    plt.title(f'Significant Wave Height Comparison for All Buoys ({model_name} {range_label})')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_path = os.path.join(range_dir, f'all_buoys_combined_{range_label}_hs_plot.png')
    plt.savefig(plot_path)
    plt.close()
    print(f"HS time series plot saved as {plot_path}")

    plt.figure(figsize=(12, 8))
    plt.scatter(combined_data['time_wind'], combined_data['model_wind'], label='Model Wind', marker='o')
    plt.scatter(combined_data['time_wind'], combined_data['obs_wind'], label='Observed Wind', marker='x')
    plt.xlabel('Time')
    plt.ylabel('Wind Speed (m/s)')
    plt.title(f'Wind Speed Comparison for All Buoys ({model_name} {range_label})')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_path = os.path.join(range_dir, f'all_buoys_combined_{range_label}_wind_plot.png')
    plt.savefig(plot_path)
    plt.close()
    print(f"Wind time series plot saved as {plot_path}")

    smr_stats_model_hs = mvalstats.smrstat(combined_model_hs)
    smr_stats_obs_hs = mvalstats.smrstat(combined_obs_hs)
    metrics_stats_hs = mvalstats.metrics(combined_model_hs, combined_obs_hs)

    smr_stats_model_wind = mvalstats.smrstat(combined_model_wind)
    smr_stats_obs_wind = mvalstats.smrstat(combined_obs_wind)
    metrics_stats_wind = mvalstats.metrics(combined_model_wind, combined_obs_wind)

    stats_df_hs = pd.DataFrame({
        'Metric': ['Mean', 'Variance', 'Skewness', 'Kurtosis', 'Min', 'Max', 'Percentile80', 'Percentile90', 'Percentile95', 'Percentile99', 'Percentile99.9'],
        'Model': smr_stats_model_hs,
        'Observation': smr_stats_obs_hs
    })

    metrics_df_hs = pd.DataFrame({
        'Metric': ['Bias', 'RMSE', 'Normalized Bias', 'Normalized RMSE', 'Scatter Component of RMSE', 'Scatter Index', 'HH', 'Correlation Coefficient', 'Number of Observations'],
        'Value': metrics_stats_hs
    })

    stats_df_wind = pd.DataFrame({
        'Metric': ['Mean', 'Variance', 'Skewness', 'Kurtosis', 'Min', 'Max', 'Percentile80', 'Percentile90', 'Percentile95', 'Percentile99', 'Percentile99.9'],
        'Model': smr_stats_model_wind,
        'Observation': smr_stats_obs_wind
    })

    metrics_df_wind = pd.DataFrame({
        'Metric': ['Bias', 'RMSE', 'Normalized Bias', 'Normalized RMSE', 'Scatter Component of RMSE', 'Scatter Index', 'HH', 'Correlation Coefficient', 'Number of Observations'],
        'Value': metrics_stats_wind
    })

    stats_file = os.path.join(range_dir, f'all_buoys_combined_{range_label}_statistics.xlsx')
    with pd.ExcelWriter(stats_file, engine='xlsxwriter') as writer:
        stats_df_hs.to_excel(writer, sheet_name='HS Stats', index=False)
        metrics_df_hs.to_excel(writer, sheet_name='HS Metrics', index=False)
        stats_df_wind.to_excel(writer, sheet_name='Wind Stats', index=False)
        metrics_df_wind.to_excel(writer, sheet_name='Wind Metrics', index=False)
    print(f"Statistics saved to {stats_file}")

    return combined_data, combined_model_hs, combined_obs_hs, combined_model_wind, combined_obs_wind, smr_stats_model_hs, metrics_stats_hs, smr_stats_model_wind, metrics_stats_wind

def create_combined_taylor_plot(data_dict, forecast_range, output_dir, variable):
    suffixes = ['hr3a', 'hr3b']
    sdev = []
    crmsd = []
    ccoef = []
    model_data = []
    obs_data = None

    # Collect model and observation data
    for model_name in suffixes:
        if model_name in data_dict:
            model_var = data_dict[model_name][1] if variable == 'hs' else data_dict[model_name][3]
            obs_var = data_dict[model_name][2] if variable == 'hs' else data_dict[model_name][4]
            print(f"Model {model_name} {variable} data shape: {model_var.shape}")
            print(f"Observation {variable} data shape: {obs_var.shape}")
            model_data.append(model_var)
            if obs_data is None:
                obs_data = obs_var

            # Calculate statistics for each model separately , imp
            model_sdev = np.std(model_var)
            model_crmsd = np.sqrt(np.mean((model_var - obs_var) ** 2))
            model_ccoef = np.corrcoef(model_var, obs_var)[0, 1]

            sdev.append(model_sdev)
            crmsd.append(model_crmsd)
            ccoef.append(model_ccoef)

    # Making sure all model data arrays are the same length :)
    min_length = min(len(md) for md in model_data)
    print(f"Minimum length of model data arrays: {min_length}")
    model_data = [md[:min_length] for md in model_data]
    obs_data = obs_data[:min_length]

    # Convert model_data to a numpy array
    model_data = np.array(model_data)

    # Add observation statistics to the lists
    sdev = [np.std(obs_data)] + sdev
    crmsd = [0] + crmsd
    ccoef = [1] + ccoef

    print(f"sdev: {sdev}")
    print(f"crmsd: {crmsd}")
    print(f"ccoef: {ccoef}")

    # Create ModelObsPlot for the variable
    mop = ModelObsPlot(
        model=model_data.T,
        obs=obs_data,
        axisnames=["Models", "Observations"],
        mlabels=suffixes,
        ftag=os.path.join(output_dir, f"plot_{variable.upper()}_{forecast_range}_Satellite_Season")
    )

    mop.qqplot()
    mop.taylordiagram(sdev=sdev, crmsd=crmsd, ccoef=ccoef)

    # Save the correlation coefficients
    correlation_coefficients = ccoef[1:]  
    cc_df = pd.DataFrame({
        'Model': suffixes,
        'Correlation Coefficient': correlation_coefficients
    })

    cc_file = os.path.join(output_dir, f'correlation_coefficients_{variable}_{forecast_range}.csv')
    cc_df.to_csv(cc_file, index=False)
    print(f"Correlation coefficients saved to {cc_file}")

common_buoy_ids = get_common_buoy_ids(model_paths)
if not common_buoy_ids:
    print("No common buoy IDs found across all models.")
else:
    all_model_data = {}
    for model, model_dir in model_paths.items():
        for start, end in forecast_ranges:
            result = process_model_data(model, model_dir, start, end, common_buoy_ids)
            if result is None:
                continue
            combined_data, combined_model_hs, combined_obs_hs, combined_model_wind, combined_obs_wind, smr_stats_model_hs, metrics_stats_hs, smr_stats_model_wind, metrics_stats_wind = result
            range_label = f"{start}to{end}hrs"
            if range_label not in all_model_data:
                all_model_data[range_label] = {}
            all_model_data[range_label][model] = (combined_data, combined_model_hs, combined_obs_hs, combined_model_wind, combined_obs_wind, smr_stats_model_hs, metrics_stats_hs, smr_stats_model_wind, metrics_stats_wind)

    if plot_combined_taylor:
        for range_label, data_dict in all_model_data.items():
            create_combined_taylor_plot(data_dict, range_label, directory_path, 'hs')
            create_combined_taylor_plot(data_dict, range_label, directory_path, 'wind')

