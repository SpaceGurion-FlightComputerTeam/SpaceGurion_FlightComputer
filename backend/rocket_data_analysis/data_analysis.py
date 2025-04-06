import random
import csv
import time
import numpy as np
import os
import asyncio
import math
import json
import websockets

CLIENTS = set() # Set to keep track of connected WebSocket clients



# This function simulates realistic data generation for temperature, pressure, altitude, gyro, and accelerometer values.
# TODO: Replace with actual sensor data acquisition function
def generate_realistic_data(iteration):
    time_elapsed = iteration * 1.0
    temperature = 15 + 5 * np.sin(time_elapsed / 10) + random.uniform(-1, 1)
    pressure = 100 + 50 * np.cos(time_elapsed / 20) + random.uniform(-5, 5)
    altitude = time_elapsed * 10 + random.uniform(-10, 10)
    if altitude > 2000:
        altitude = 2000

    gyro_x = np.sin(time_elapsed / 5) * 2 + random.uniform(-0.5, 0.5)
    gyro_y = np.cos(time_elapsed / 7) * 2 + random.uniform(-0.5, 0.5)
    gyro_z = np.sin(time_elapsed / 3) * 3 + random.uniform(-1, 1)

    accel_x = np.cos(time_elapsed / 8) * 2 + random.uniform(-0.5, 0.5)
    accel_y = np.sin(time_elapsed / 6) * 2 + random.uniform(-0.5, 0.5)
    accel_z = np.cos(time_elapsed / 4) * 12 + random.uniform(-2, 10)

    return temperature, pressure, altitude, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z


# Broadcast JSON data to all connected clients
# This function sends the data to GUI visualization in real-time.
async def broadcast(data_dict):
    if CLIENTS:
        message = json.dumps(data_dict)
        await asyncio.wait([client.send(message) for client in CLIENTS])

# WebSocket handler: Handles incoming WebSocket connections
# This function is called when a new client connects to the WebSocket server.
async def websocket_handler(websocket):
    CLIENTS.add(websocket)              # Add the new client to the set of connected clients
    try:
        await websocket.wait_closed()   # Wait for the client to close the connection 
    finally:
        CLIENTS.remove(websocket)       # Remove the client from the set of connected clients


# Async function to read, write and stream data
async def read_and_write_data():
    csv_file = 'backend/rocket_data_analysis/rocket_data.csv'  # Create a CSV file to store the data
    if os.path.isfile(csv_file):   # Check if the file already exists
        os.remove(csv_file)

    # Create a new CSV file and write the header
    ############## TODO: Decide on a uniform format for the data JSON + add GPS data columns ###############
    # current format is: [Timestamp, Temperature, Pressure, Altitude, Gyro X, Gyro Y, Gyro Z, Accel X, Accel Y, Accel Z]
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Temperature', 'Pressure', 'Altitude',
                         'Gyro X', 'Gyro Y', 'Gyro Z', 'Accel X', 'Accel Y', 'Accel Z'])
        file.flush()    # Ensure the header is written immediately

    iteration = 0   # Initialize iteration counter for data generation. delete this line if not needed
    start_time = time.time()

    try:
        # Main loop to write data to CSV and broadcast to WebSocket clients
        # TODO: Handle iteration differently if needed. Currently, it runs for 10000 iterations.
        while iteration < 10000:
            data = generate_realistic_data(iteration)  # replace with actual sensor data acquisition function
            timestamp = time.time() - start_time
            formatted_data = [f"{timestamp:.3f}"] + [f"{value:.3f}" for value in data]  # Format data to 3 decimal places, change if needed
            with open(csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(formatted_data) # Write the data to the CSV file
                file.flush()  # Ensure the data is written immediately
            
            # Send the data to WebSocket clients using JSON format, change to uniform format if needed
            json_data = {
                "Timestamp": formatted_data[0],
                "Temperature": formatted_data[1],
                "Pressure": formatted_data[2],
                "Altitude": formatted_data[3],
                "Gyro X": formatted_data[4],
                "Gyro Y": formatted_data[5],
                "Gyro Z": formatted_data[6],
                "Accel X": formatted_data[7],
                "Accel Y": formatted_data[8],
                "Accel Z": formatted_data[9],
            }
            await broadcast(json_data)  # Broadcast the data to all connected clients
            print(f"Broadcasting data: {json_data}")   # log for debugging (optional)
    
            iteration += 1              # Increment the iteration counter
            await asyncio.sleep(0.1)    # add a small delay to simulate real-time data generation

    except asyncio.CancelledError:
        print("Process interrupted.")
