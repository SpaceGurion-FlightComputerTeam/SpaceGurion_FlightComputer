import random
import csv
import time
import numpy as np
import os
import asyncio
import math
import json
from GroundTelemetryReciever import serial_line_generator
# import websockets

CLIENTS = set() # Set to keep track of connected WebSocket clients
is_reading = False # Flag to indicate if data is being read and written
is_connected = False # Flag to indicate if the sensor is connected

# This function simulates realistic data generation for temperature, pressure, altitude, gyro, and accelerometer values.
# TODO: Replace with actual sensor data acquisition function
def generate_realistic_data(iteration, dt=0.1):
    """
    Generate realistic sensor data for a model rocket flight.
    
    Parameters:
        iteration: Current iteration (used to calculate flight time)
        dt: Time step between iterations in seconds (default: 0.1)
    
    Returns:
        Tuple of sensor readings: temperature, pressure, altitude, 
        gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z
    """
    # Calculate flight time
    time_elapsed = iteration * dt
    
    # Flight phases (in seconds)
    launch_phase = 2.0
    powered_ascent = 5.0
    coast_phase = 15.0
    descent_phase = 40.0
    
    # Base environmental values
    base_temp = 15.0  # degrees Celsius
    base_pressure = 101.3  # kPa (sea level)
    
    # Determine flight phase and calculate altitude
    if time_elapsed < launch_phase:
        # Launch phase - sitting on pad or initial launch
        altitude = 0.1 * time_elapsed**2 + random.uniform(-0.1, 0.1)
        accel_z = 15.0 + random.uniform(-1, 1)
        
    elif time_elapsed < (launch_phase + powered_ascent):
        # Powered ascent - rapid acceleration upward
        altitude = 50 * (time_elapsed - launch_phase)**2 + random.uniform(-1, 2)
        accel_z = 30.0 + random.uniform(-3, 3)
        
    elif time_elapsed < (launch_phase + powered_ascent + coast_phase):
        # Coast phase - decreasing vertical acceleration, increasing horizontal drift
        t = time_elapsed - (launch_phase + powered_ascent)
        altitude = 50 * powered_ascent**2 + 80 * t - 9.8 * t**2/2 + random.uniform(-2, 2)
        accel_z = -9.8 + random.uniform(-1, 1)  # Gravity plus fluctuations
        
    else:
        # Descent phase - parachute deployed
        t = time_elapsed - (launch_phase + powered_ascent + coast_phase)
        max_altitude = 50 * powered_ascent**2 + 80 * coast_phase - 9.8 * coast_phase**2/2
        descent_factor = np.exp(-0.1 * t)  # Exponential decay for parachute descent
        altitude = max(0, max_altitude * descent_factor) + random.uniform(-5, 5)
        accel_z = -2.0 + random.uniform(-0.5, 0.5)  # Slower descent due to parachute
    
    # Cap altitude at maximum
    altitude = min(altitude, 2000)
    
    # Temperature: slowly decreases with altitude (~6.5°C/km) + some noise
    temperature = base_temp - (altitude / 1000 * 6.5) + random.uniform(-0.5, 0.5)
    
    # Pressure decreases with altitude (simplified barometric formula)
    pressure = base_pressure * np.exp(-0.00012 * altitude) + random.uniform(-0.2, 0.2)
    
    # Gyroscope data - higher oscillations during powered flight, dampening during descent
    if time_elapsed < (launch_phase + powered_ascent):
        # More wobble during powered ascent
        intensity = 2.0
    elif time_elapsed < (launch_phase + powered_ascent + coast_phase):
        # Less wobble during coast
        intensity = 1.0
    else:
        # Slow rotation during descent (parachute effect)
        intensity = 0.5
    
    gyro_x = np.sin(time_elapsed / 2) * intensity + random.uniform(-0.2, 0.2)
    gyro_y = np.cos(time_elapsed / 3) * intensity + random.uniform(-0.2, 0.2)
    gyro_z = np.sin(time_elapsed / 5) * intensity * 1.5 + random.uniform(-0.3, 0.3)
    
    # Accelerometer data (x and y components simulate drift and wind effects)
    accel_x = np.sin(time_elapsed / 7) * 1.5 + random.uniform(-0.5, 0.5)
    accel_y = np.cos(time_elapsed / 9) * 1.5 + random.uniform(-0.5, 0.5)
    
    return temperature, pressure, altitude, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z

#Receive Telemtry Data And Export 
def TelemetryToJson():
    #Receive Telemetry Data
    for line in serial_line_generator():
        print(f"Received: {line}")


# Broadcast JSON data to all connected clients
# This function sends the data to GUI visualization in real-time.
async def broadcast(data_dict):
    if CLIENTS:
        message = json.dumps(data_dict)
        await asyncio.wait([client.send(message) for client in CLIENTS])

# WebSocket handler: Handles incoming WebSocket connections
# This function is called when a new client connects to the WebSocket server.
async def websocket_handler(websocket):
    global is_reading, is_connected
    CLIENTS.add(websocket)  # Add the new client to the set of connected clients
    
    async for message in websocket:
        data = json.loads(message)
        cmd = data.get("command")
        if cmd == "connect":
            # Attempt to connect to sensor here
            success = try_connect_to_sensors()  # Simulate a successful connection (replace with actual connection logic)
            if success:
                is_connected = True
                await websocket.send(json.dumps({"status": "connected"}))
                print("[Backend] Sensor connected successfully.")
            else:
                await websocket.send(json.dumps({"status": "connection_failed"}))
        elif cmd == "start":
            is_reading = True
            print("Data generation started.")
        elif cmd == "stop":
            is_reading = False
            print("Data generation stopped.")
    try:
        await websocket.wait_closed()   # Wait for the client to close the connection 
    finally:
        CLIENTS.remove(websocket)       # Remove the client from the set of connected clients

async def try_connect_to_sensors():
    try:
        # Replace with actual hardware init logic (e.g., open serial port)
        # Example:
        # serial_port = serial.Serial('COM3', 115200, timeout=1)
        # time.sleep(2)  # wait for connection
        print("[Backend] Simulating connection to sensors...")
        await asyncio.sleep(1)  # simulate delay
        return True  # return False if connection fails
    except Exception as e:
        print(f"[Backend] Sensor connection failed: {e}")
        return False

# Async function to read, write and stream data
async def read_and_write_data():
    csv_file = 'backend/rocket_data_analysis/rocket_data.csv'  # Create a CSV file to store the data
    if os.path.isfile(csv_file):   # Check if the file already exists
        os.remove(csv_file)

    # Create a new CSV file and write the header
    ############## TODO: Decide on a uniform format for the data JSON + add GPS data columns ###############
    # current format is:[Temp,Pressure,Altitude,ax,ay,az,gx,gy,gz,mx,my,mz,latitude,longtitude]
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Temperature', 'Pressure', 'Altitude',
                        'Gyro X', 'Gyro Y', 'Gyro Z', 'Accel X', 'Accel Y', 'Accel Z'])
        file.flush()    # Ensure the header is written immediately

   
    iteration = 0   # Initialize iteration counter for data generation. delete this line if not needed
    start_time = time.time()
    
    # Main loop to write data to CSV and broadcast to WebSocket clients
    while True:
        try:
            data = generate_realistic_data(iteration)  # replace with actual sensor data acquisition function
            timestamp = time.time() - start_time
            formatted_data = [f"{timestamp:.3f}"] + [f"{value:.3f}" for value in data]  # Format data to 3 decimal places, change if needed
            if is_reading:
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
            break
        
    
TelemetryToJson()
