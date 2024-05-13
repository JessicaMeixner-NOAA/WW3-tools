"""
If you want to run this code simply type python ppp1(This code name).py -m ./gfswave.t00z.global.0p25.f228.grib2.nc(the model file) -s ./Altimeter_CRYOSAT2_HRsummer.nc(the satellite data)
in your terminal.

"""

import argparse
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt

def load_unix_times(nc_file, time_var_name='time'):
    """ Load Unix times from a NetCDF file. """
    with nc.Dataset(nc_file, 'r') as data:
        times = data.variables[time_var_name][:]
    return times

def main(model_file, satellite_file):
    # Load Unix times and significant wave height data from both datasets
    altimeter_nc = nc.Dataset(satellite_file, 'r')
    altimeter_times = load_unix_times(satellite_file)
    hs_obs = altimeter_nc.variables['hs_cal'][:]
    lats_obs = altimeter_nc.variables['latitude'][:]
    lons_obs = altimeter_nc.variables['longitude'][:]

    model_nc = nc.Dataset(model_file, 'r')
    model_times = load_unix_times(model_file)
    lats_model = model_nc.variables['latitude'][:]
    lons_model = model_nc.variables['longitude'][:]
    hs_model = model_nc.variables['HTSGW_surface'][0, :, :]  

    # Efficient matching using broadcasting
    time_diffs = np.abs(altimeter_times[:, np.newaxis] - model_times)
    min_diffs = np.min(time_diffs, axis=1)
    match_indices = np.where(min_diffs <= 20)[0]  # any seconds/ hours threshold
    model_match_indices = np.argmin(time_diffs[match_indices], axis=1)

    # Extract matched data points
    matched_hs_obs = hs_obs[match_indices]
    matched_lats = lats_obs[match_indices]
    matched_lons = lons_obs[match_indices]
    matched_hs_model = [hs_model[int(np.searchsorted(lats_model, lat)), int(np.searchsorted(lons_model, lon))] for lat, lon in zip(matched_lats, matched_lons)]

    # Print matched data points
    for idx, (time_idx, mod_idx) in enumerate(zip(match_indices, model_match_indices)):
        print(f"Match {idx+1}:")
        print(f"   Time: {altimeter_times[time_idx]} (Altimeter) ~ {model_times[mod_idx]} (Model)")
        print(f"   Location: Latitude {matched_lats[idx]}, Longitude {matched_lons[idx]}")
        print(f"   Altimeter Wave Height: {matched_hs_obs[idx]} m")
        print(f"   Model Wave Height: {matched_hs_model[idx]} m\n")

    # Calculate the buffer around the matched data points
    buffer = 0.1  # Adjust as needed
    min_lon = np.min(matched_lons) - buffer
    max_lon = np.max(matched_lons) + buffer
    min_lat = np.min(matched_lats) - buffer
    max_lat = np.max(matched_lats) + buffer

    # Determine the range for the color scale to cover both datasets
    min_wave_height = min(np.min(hs_model), np.min(matched_hs_obs))
    max_wave_height = max(np.max(hs_model), np.max(matched_hs_obs))

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot the model wave height data with unified color scale
    im = ax.pcolormesh(lons_model, lats_model, hs_model, cmap='viridis', vmin=min_wave_height, vmax=max_wave_height)
    cbar = fig.colorbar(im, ax=ax, orientation='vertical', label='Significant Wave Height (m)')

    # Plot the matched significant wave heights from the altimeter data with the same color scale
    scatter = ax.scatter(matched_lons, matched_lats, c=matched_hs_obs, cmap='viridis', vmin=min_wave_height, vmax=max_wave_height, s=50, edgecolor='black', linewidth=1)

    # Set the extent of the plot
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)

    # Add labels and legend
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.colorbar(scatter, ax=ax, label='Significant Wave Height (m)')
    plt.title('Global Significant Wave Height: Model vs Altimeter Matched Observations')

    plt.savefig('matched_wave_heights_map_zoomed.png', dpi=300, bbox_inches='tight')  # Save the figure
   # plt.show()  # Display the figure on the screen

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Plot matched wave heights between model and altimeter data.')
    parser.add_argument('-m', '--model', type=str, help='Path to the model data file')
    parser.add_argument('-s', '--satellite', type=str, help='Path to the satellite data file')
    args = parser.parse_args()

    # Call the main function with specified model and satellite data files
    main(args.model, args.satellite)

