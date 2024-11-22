from datetime import datetime
import random
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
import os


# Function to generate more realistic random data
def generate_realistic_data(iteration):
    # Simulate realistic changes over time
    time_elapsed = iteration * 1.0  # Simulated time (in seconds)

    # Simulate temperature, pressure, and altitude
    temperature = 15 + 5 * np.sin(time_elapsed / 10) + random.uniform(-1, 1)
    pressure = 100 + 50 * np.cos(time_elapsed / 20) + random.uniform(-5, 5)
    altitude = time_elapsed * 5 + random.uniform(-10, 10)
    if altitude > 2000:
        altitude = 2000

    # Simulate gyro and accelerometer data
    gyro_x = np.sin(time_elapsed / 5) * 2 + random.uniform(-0.5, 0.5)
    gyro_y = np.cos(time_elapsed / 7) * 2 + random.uniform(-0.5, 0.5)
    gyro_z = np.sin(time_elapsed / 3) * 3 + random.uniform(-1, 1)

    accel_x = np.cos(time_elapsed / 8) * 2 + random.uniform(-0.5, 0.5)
    accel_y = np.sin(time_elapsed / 6) * 2 + random.uniform(-0.5, 0.5)
    accel_z = np.cos(time_elapsed / 4) * 12 + random.uniform(-2, 10)  # Acceleration z from -2g to 10g

    # return random fake data for testing
    return temperature, pressure, altitude, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z


# Write data to CSV file
def write_to_csv(data, csv_file):
    # Add data to existing file
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Initialize Headers
            writer.writerow(["Timestamp", "Temperature", "Pressure", "Altitude",
                             "Gyro X", "Gyro Y", "Gyro Z", "Accel X", "Accel Y", "Accel Z"])
        writer.writerow(data)


# Plot data from CSV file
def plot_data_from_csv(csv_file, save_plots=True):
    # Load data from CSV to npArray
    data = np.genfromtxt(csv_file, delimiter=',', skip_header=1)

    # # If data is 1D and has one row, reshape it to 2D
    # if data.ndim == 1:
    #     data = np.expand_dims(data, axis=0)

    if data.size == 0:
        print("No data to plot.")
        return

    # Extract data from each column
    timestamps = data[:, 0]
    temperatures = data[:, 1]
    pressures = data[:, 2]
    altitudes = data[:, 3]
    gyro_x = data[:, 4]
    gyro_y = data[:, 5]
    gyro_z = data[:, 6]
    accel_x = data[:, 7]
    accel_y = data[:, 8]
    accel_z = data[:, 9]

    # fixed steps size, plots around 20 points
    num_points = len(timestamps)
    indices = np.arange(0, num_points, max(1, num_points // 20))

    plt.ion()  # dynamic mode
    plt.figure(figsize=(14, 12))

    # Plot Temperature
    plt.subplot(3, 3, 1)
    plt.plot(timestamps[indices], temperatures[indices], 'r-', label='Temperature')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature')
    plt.legend(loc='upper right')
    plt.title('Temperature Over Time')
    plt.grid(True)

    # Plot Pressure
    plt.subplot(3, 3, 2)
    plt.plot(timestamps[indices], pressures[indices], 'b-', label='Pressure')
    plt.xlabel('Time (s)')
    plt.ylabel('Pressure')
    plt.legend(loc='upper right')
    plt.title('Pressure Over Time')
    plt.grid(True)

    # Plot Altitude
    plt.subplot(3, 3, 3)
    plt.plot(timestamps[indices], altitudes[indices], 'g-', label='Altitude')
    plt.xlabel('Time (s)')
    plt.ylabel('Altitude')
    plt.legend(loc='upper right')
    plt.title('Altitude Over Time')
    plt.grid(True)

    # Plot Gyro X
    plt.subplot(3, 3, 4)
    plt.plot(timestamps[indices], gyro_x[indices], 'c-', label='Gyro X')
    plt.xlabel('Time (s)')
    plt.ylabel('Gyro X')
    plt.legend(loc='upper right')
    plt.title('Gyro X Over Time')
    plt.grid(True)

    # Plot Gyro Y
    plt.subplot(3, 3, 5)
    plt.plot(timestamps[indices], gyro_y[indices], 'm-', label='Gyro Y')
    plt.xlabel('Time (s)')
    plt.ylabel('Gyro Y')
    plt.legend(loc='upper right')
    plt.title('Gyro Y Over Time')
    plt.grid(True)

    # Plot Gyro Z
    plt.subplot(3, 3, 6)
    plt.plot(timestamps[indices], gyro_z[indices], 'y-', label='Gyro Z')
    plt.xlabel('Time (s)')
    plt.ylabel('Gyro Z')
    plt.legend(loc='upper right')
    plt.title('Gyro Z Over Time')
    plt.grid(True)

    # Plot Accel X
    plt.subplot(3, 3, 7)
    plt.plot(timestamps[indices], accel_x[indices], 'o-', label='Accel X')
    plt.xlabel('Time (s)')
    plt.ylabel('Accel X')
    plt.legend(loc='upper right')
    plt.title('Accel X Over Time')
    plt.grid(True)

    # Plot Accel Y
    plt.subplot(3, 3, 8)
    plt.plot(timestamps[indices], accel_y[indices], 'ko-', label='Accel Y')
    plt.xlabel('Time (s)')
    plt.ylabel('Accel Y')
    plt.legend(loc='upper right')
    plt.title('Accel Y Over Time')
    plt.grid(True)

    # Plot Accel Z
    plt.subplot(3, 3, 9)
    plt.plot(timestamps[indices], accel_z[indices], 'o-', color='orange', label='Accel Z')
    plt.xlabel('Time (s)')
    plt.ylabel('Accel Z')
    plt.legend(loc='upper right')
    plt.title('Accel Z Over Time')
    plt.grid(True)

    plt.tight_layout()  # Adjust layout

    # Automatically adjust y-axis scaling limits
    plt.autoscale(enable=True, axis='y')

    # Optionally save the plot
    if save_plots:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(os.path.join(plot_dir, f'rocket_data_plots_{current_time}.png'))
        plt.close()
        print(f"Plot saved to Directory")

    plt.ioff()  # Disable interactive mode
    # plt.show()  # Show the plot window


# Main function to collect data and run the process
# Function that clears plot directory
def clear_plot_directory(plt_dir):
    files = os.listdir(plt_dir)
    for file in files:
        os.remove(os.path.join(plt_dir, file))


# Directory where plots are saved
plot_dir = 'plots/'
# Create the directory if it doesn't exist
os.makedirs(plot_dir, exist_ok=True)
clear_plot_directory(plot_dir)  # clears the directory from previous runs

# Clear existing CSV file if it exists
csv_file = 'rocket_data.csv'
if os.path.isfile(csv_file):
    os.remove(csv_file)

# Open a CSV file to write the data
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Temperature', 'Pressure', 'Altitude',
                     'Gyro X', 'Gyro Y', 'Gyro Z', 'Accel X', 'Accel Y', 'Accel Z'])
    file.flush()  # Flush to ensure header is written immediately

# Collect data in a running while loop
iteration = 0
start_time = time.time()  # Record the start time

try:
    while True:
        # Generate realistic random data
        data = generate_realistic_data(iteration)

        # Write the data to the CSV file immediately
        timestamp = time.time() - start_time  # holds the elapsed time since the start
        formatted_data = [f"{timestamp:.3f}"] + [f"{value:.3f}" for value in data]
        write_to_csv(formatted_data, csv_file)

        # Print the data (optional)
        print(f"Time: {formatted_data[0]},"
              f"Temperature: {formatted_data[1]}, Pressure: {formatted_data[2]}, Altitude: {formatted_data[3]}, "
              f"Gyro X: {formatted_data[4]}, Gyro Y: {formatted_data[5]}, Gyro Z: {formatted_data[6]}, "
              f"Accel X: {formatted_data[7]}, Accel Y: {formatted_data[8]}, Accel Z: {formatted_data[9]}")

        # Increment iteration counter
        iteration += 1

        # Plot and save the data every x iterations
        if iteration % 100 == 0:
            plot_data_from_csv(csv_file)

        # stop condition (for checking only)
        if iteration == 10000:
            print("stop")
            break

        # Sleep for a short time before next iteration
        time.sleep(0.1)  # 10Hz frequency, adjust as needed


except KeyboardInterrupt:
    print("Process interrupted by user. Exiting...")
