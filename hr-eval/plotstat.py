import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# File paths for all uploaded Excel files
file_paths = {
    'MULTI1': './summer_stats_MULTI1.csv',
    'GFSv16': './summer_stats_GFSv16.csv',
    'HR1': './summer_stats_HR1.csv',
    'HR2': './summer_stats_HR2.csv',
    'HR3a': './summer_stats_HR3a.csv',
    'HR3b': './summer_stats_HR3b.csv'
}

# Load all files into DataFrames
dataframes = {model: pd.read_csv(path) for model, path in file_paths.items()}

# Normalize the 'Day' column to extract numeric values and combine all data into one DataFrame
for model, df in dataframes.items():
    df['Day'] = df['File'].str.extract('(\d+)').astype(int)  # Extract day number and convert to integer
    df['Model'] = model  # Add model name for identification

# Combine all DataFrames
combined_data = pd.concat(dataframes.values(), ignore_index=True)

# Sort the combined data by 'Day'
sorted_data = combined_data.sort_values(by='Day')

# Find the minimum number of days for which all models have data
max_days_per_model = sorted_data.groupby('Model')['Day'].max()
min_common_day = max_days_per_model.min()

# Plotting function for each metric
def plot_sorted_metric(metric, use_common_days_only=False):
    plt.figure(figsize=(10, 6))
    model_colors = {
        'MULTI1': 'darkred',
        'GFSv16': 'blue',
        'HR1': 'darkgreen',
        'HR2': 'darkorange',
        'HR3a': 'deeppink',
        'HR3b': 'purple'
    }
    for model in sorted_data['Model'].unique():
        model_data = sorted_data[sorted_data['Model'] == model]
        if use_common_days_only:
            model_data = model_data[model_data['Day'] <= min_common_day]
        plt.plot((model_data['Day'] / 24) + 1, model_data[metric], marker='o', label=model, color=model_colors[model])  # +1 to start from Day 1
    plt.title(f'{metric} Comparison by Day')
    plt.xlabel('Day')
    plt.ylabel(metric)

    # Adjust the x-axis for day display, starting from Day 1
    day_conversion_factor = 24
    tick_spacing = 1  # Days between labels
    if use_common_days_only:
        max_day = int(min_common_day / day_conversion_factor) + 1
    else:
        max_day = int(sorted_data['Day'].max() / day_conversion_factor) + 1
    ticks = np.arange(1, max_day + 1, tick_spacing)  # Adjust to show from Day 1
    labels = [f'Day {tick}' for tick in ticks]
    plt.xticks(ticks, labels)

    plt.legend()
    plt.grid(True)
    plt.savefig(f'./{metric}.png')
    plt.close()

# Metrics to be plotted
metrics = ['WND Normalized Bias', 'WND Normalized RMSE', 'WND CC', 'WND SI']
#metrics = ['HS Normalized Bias', 'HS Normalized RMSE', 'HS CC', 'HS SI']

# Switch to control plotting behavior
plot_up_to_min_common_day = True  # Set to False to plot up to the full range available for each model

for metric in metrics:
    plot_sorted_metric(metric, use_common_days_only=plot_up_to_min_common_day)

