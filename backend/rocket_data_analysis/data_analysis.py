import random
import csv
import time
import numpy as np
import os
import asyncio
import math
import json
from rocket_data_analysis.GroundTelemetryReciever import serial_line_generator
# import websockets

CLIENTS = set() # Set to keep track of connected WebSocket clients
is_reading = False # Flag to indicate if data is being read and written
is_connected = False # Flag to indicate if the sensor is connected

# This function simulates realistic data generation for temperature, pressure, altitude, gyro, and accelerometer values.
# TODO: Replace with actual sensor data acquisition function
def generate_realistic_data(iteration, dt=0.1):
    """
    Generate realistic sensor data for a ~1 km model rocket flight.
    
    Phases:
      1. Pad (0–1 s): rocket sits, small vibrations
      2. Powered ascent (1–4 s): high upward accel from motor
      3. Coast (4–14 s): rise under gravity, then begin descent
      4. Parachute descent (14–54 s): slow descent at terminal velocity
    
    Returns a dict of:
        Temperature (°C), Pressure (kPa), Altitude (m),
        Accel X/Y/Z (m/s²), Gyro X/Y/Z (°/s),
        Mag X/Y/Z (μT), Latitude, Longitude
    """
    # Time
    t = iteration * dt

    # Phase durations
    t_pad = 1.0
    t_burn = 3.0
    t_coast = 10.0
    t_descent = 40.0
    total = t_pad + t_burn + t_coast + t_descent

    # Base environmental constants
    T0 = 288.15       # Sea‐level temperature (K)
    L = 0.0065        # Temperature lapse rate (K/m)
    P0 = 101.325      # Sea‐level pressure (kPa)
    g0 = 9.80665      # Gravity (m/s²)
    R = 287.05        # Specific gas constant for dry air (J/(kg·K))

    # Launch site
    launch_lat = 37.8651
    launch_lon = -119.5383

    # Kinematic state
    # Precompute end‐of‐burn velocity & altitude
    a_burn = 30.0               # avg thrust accel (m/s²)
    v_burn_end = a_burn * t_burn
    h_burn_end = 0.5 * a_burn * t_burn**2

    # Altitude, velocity, acceleration
    if t < t_pad:
        # Pad: small random shake around 0
        altitude = 0.0
        velocity = 0.0
        accel_z = g0 + random.uniform(-0.2, 0.2)
    elif t < t_pad + t_burn:
        # Powered ascent
        tb = t - t_pad
        altitude = 0.5 * a_burn * tb**2
        velocity = a_burn * tb
        accel_z = a_burn + random.uniform(-2, 2)
    elif t < t_pad + t_burn + t_coast:
        # Coast up then begin descent under gravity
        tc = t - (t_pad + t_burn)
        # vertical velocity under gravity
        velocity = v_burn_end - g0 * tc
        altitude = h_burn_end + v_burn_end * tc - 0.5 * g0 * tc**2
        accel_z = -g0 + random.uniform(-0.5, 0.5)
    else:
        # Parachute descent at approx terminal velocity ~5 m/s
        td = t - (t_pad + t_burn + t_coast)
        altitude_coast_end = max(0, h_burn_end + v_burn_end * t_coast - 0.5 * g0 * t_coast**2)
        v_term = 5.0  # m/s
        altitude = max(0, altitude_coast_end - v_term * td)
        velocity = -v_term
        accel_z = random.uniform(-0.3, 0.3)

    # Clamp
    altitude = max(0.0, altitude)

    # Horizontal small jitter on pad/coast, wind drift later
    if t < t_pad:
        accel_x = random.uniform(-0.2, 0.2)
        accel_y = random.uniform(-0.2, 0.2)
    else:
        accel_x = random.uniform(-1.0, 1.0)
        accel_y = random.uniform(-1.0, 1.0)

    # Gyros simulate small oscillations + initial roll torque
    if t < t_pad:
        gyro_x = random.uniform(-0.1, 0.1)
        gyro_y = random.uniform(-0.1, 0.1)
        gyro_z = random.uniform(-0.1, 0.1)
    elif t < t_pad + t_burn:
        gyro_x = 20.0 * math.sin(5* (t - t_pad)) + random.uniform(-1, 1)
        gyro_y = 20.0 * math.cos(4* (t - t_pad)) + random.uniform(-1, 1)
        gyro_z = 50.0 * math.exp(-0.5*(t - t_pad)) + random.uniform(-2, 2)
    elif t < t_pad + t_burn + t_coast:
        gyro_x = 5.0 * math.sin(2* (t - t_pad - t_burn)) + random.uniform(-0.5, 0.5)
        gyro_y = 5.0 * math.cos(2* (t - t_pad - t_burn)) + random.uniform(-0.5, 0.5)
        gyro_z = 5.0 * math.exp(-0.2*(t - t_pad - t_burn)) + random.uniform(-0.5, 0.5)
    else:
        gyro_x = random.uniform(-0.3, 0.3)
        gyro_y = random.uniform(-0.3, 0.3)
        gyro_z = random.uniform(-0.2, 0.2)

    # Barometric atmosphere model
    temperature = (T0 - L * altitude) + random.uniform(-0.5, 0.5)  # in K
    temperature_c = temperature - 273.15                         # in °C

    pressure = P0 * (temperature / T0) ** (g0 / (R * L))          # in kPa
    pressure += random.uniform(-0.1, 0.1)

    # Magnetometer (simple Earth field + noise)
    base_mag_x, base_mag_y, base_mag_z = 20.0, 0.0, 40.0
    mag_x = base_mag_x + random.uniform(-1, 1)
    mag_y = base_mag_y + random.uniform(-1, 1)
    mag_z = base_mag_z + random.uniform(-1, 1)

    # GPS drift: up to ±200 m over flight
    drift_factor = min(1.0, t / total)
    max_drift = 200.0  # meters
    angle = math.radians(45)  # wind direction
    north = max_drift * drift_factor * math.cos(angle) + random.uniform(-5, 5)
    east  = max_drift * drift_factor * math.sin(angle) + random.uniform(-5, 5)
    lat = launch_lat + (north / 111000.0)
    lon = launch_lon + (east / (111000.0 * math.cos(math.radians(launch_lat))))

    # Return all sensor readings
    json_data = {
                "time": time.time(),  # Timestamp
                
                # Barometer data
                "temp": temperature,
                "pres": pressure,
                "altitude": altitude,
                
                # IMU data
                "ax": accel_x,
                "ay": accel_y,
                "az": accel_z,
                "gx": gyro_x,
                "gy": gyro_y,
                "gz": gyro_z,
                "mx": mag_x,
                "my": mag_y,
                "mz": mag_z,
                
                # GPS data
                "latitude": lat,
                "longitude": lon
    }
    return json_data


# Broadcast JSON data to all connected clients
# This function sends the data to GUI visualization in real-time.
async def broadcast(data_dict):
    if CLIENTS:
        message = json.dumps(data_dict)
        await asyncio.wait([client.send(message) for client in CLIENTS])

# WebSocket handler: Handles incoming WebSocket connections
# This function is called when a new client connects to the WebSocket server.
# Handles buttons in the GUI (connect, start, stop, abort)
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
        elif cmd == "abort":
            # Add logic to abort the mission here
            print("Mission Aborted")
    try:
        await websocket.wait_closed()   # Wait for the client to close the connection 
    finally:
        CLIENTS.remove(websocket)       # Remove the client from the set of connected clients




frame_counter = 0   

#Receive Telemtry Data And Export 
def TelemetryToJson():
    json_data = {}
    print("[Backend] Starting telemetry data reception...")
    start_time = time.time()  # Start the timer when reading starts

    #Receive Telemetry Data
    for line in serial_line_generator():
        timestamp = time.time() - start_time
        
         # Check if the line is not empty
        if line != None:
           # Split into three sections - Barometer, IMU, GPS
            parts = line.split(";")
            if len(parts) != 3:
                raise ValueError("Line does not have three sections separated by ';'")

            # Flatten into one list of values (as strings)
            values = [timestamp]+parts[0].split(",") + parts[1].split(",") + parts[2].split(",")

            if len(values) != 15:
                raise ValueError("Expected 15 values, got {}".format(len(values)))

            # Optional: convert all to float (remove if you want strings)
            #values = [float(val) for val in values]
            
            # # Map to JSON
            json_data = {
                "time": values[0],  # Timestamp
                
                # Barometer data
                "temp": values[1],
                "pres": values[2],
                "altitude": values[3],
                
                # IMU data
                "ax": values[4],
                "ay": values[5],
                "az": values[6],
                "gx": values[7],
                "gy": values[8],
                "gz": values[9],
                "mx": values[10],
                "my": values[11],
                "mz": values[12],
                
                # GPS data
                "latitude": values[13],
                "longitude": values[14]
            }
        
        print(f"Received: {line}")
        print(f"Parsed JSON: {json_data}")
       
        yield json_data  # Yield the JSON data for further processing

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
    # current format is:[Temp,Pressure,Altitude ; ax,ay,az,gx,gy,gz,mx,my,mz ; latitude,longitude]
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Temperature', 'Pressure', 'Altitude',
                         'Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y', 'Gyro Z', 'MX', 'MY', 'MZ', 'Latitude', 'Longitude'])
        file.flush()    # Ensure the header is written immediately

   
    iteration = 0   # Initialize iteration counter for data generation. delete this line if not needed
    # Main loop to write data to CSV and broadcast to WebSocket clients
    while True:
        try:           
            #is_reading = True  # Set the flag to indicate that data is being read, for testing purposes
            if is_reading:
                json_data = generate_realistic_data(iteration)  # replace with actual sensor data acquisition function
                #for json_data in TelemetryToJson():
                formatted_data = [f"{value:.6f}" for value in json_data.values()]
                
                print(f"Formatted data: {formatted_data}") # log for debugging (optional)
                # Write the data to the CSV file
                with open(csv_file, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(formatted_data) # Write the data to the CSV file
                    file.flush()  # Ensure the data is written immediately
                # Check if the data is being read
            
                # Send the data to WebSocket clients using JSON format, change to uniform format if needed        
                await broadcast(json_data)  # Broadcast the data to all connected clients
                print(f"Broadcasting data: {json_data}")   # log for debugging (optional)
            
                iteration += 1              # Increment the iteration counter
                await asyncio.sleep(0.1)    # add a small delay to simulate real-time data generation

        except asyncio.CancelledError:
            print("Process interrupted.")
            break


#TelemetryToJson()
#asyncio.run(read_and_write_data())