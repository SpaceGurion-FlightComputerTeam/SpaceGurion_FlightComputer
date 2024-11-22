import datetime
import os
import time
import Barometer
import imuData
import GPS
# from imu import IMU
# from gps import read_gps

# Create timestamped log file
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
filename = f"sensor_data_{timestamp}.txt"
desktop_dir = "/tmp/"  # Change to your desired directory
full_path = os.path.join(desktop_dir, filename)

# Open a new file for writing
log_file = open(full_path, 'w')
log_file.write("Timestamp, Temperature (C), Pressure (hPa), Altitude (m), Gyro X, Gyro Y, Gyro Z, Accel X, Accel Y, Accel Z, Temperature (IMU), Latitude, Longitude, Altitude (GPS), Speed (knots), Satellites\n")
print(f"Log file created at '{full_path}'")

# # Initialize IMU
imuData  = imuData()
imuData.start()
# Initialize Barometer  
barometer = Barometer()

# initialize GPS
gps = GPS()


try:

    while True:
        # Read from BMP280
        bmp_temperature, bmp_pressure, bmp_altitude = barometer.read()
        LastPosition,lastSpeed , rawAccel, rawGyro = imuData.getData()
        coordinates = gps.get_coords()

        # Generate a timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gyro_x, gyro_y, gyro_z = rawGyro
        accel_x, accel_y, accel_z = rawAccel
        # Log data
        log_file.write(f"Timestamp: {timestamp}")
        log_file.write(f"Temperature: {bmp_temperature:.2f} C, Pressure: {bmp_pressure:.2f} hPa, Altitude: {bmp_altitude:.2f} m , {gyro_x}, {gyro_y}, {gyro_z}, {accel_x}, {accel_y}, {accel_z} ,  Coordinates : {coordinates}\n")
        log_file.flush()

        # Print data to console
        print(f"Timestamp: {timestamp}")
        print(f"Temperature: {bmp_temperature:.2f} C, Pressure: {bmp_pressure:.2f} hPa, Altitude: {bmp_altitude:.2f} m")

        time.sleep(1)
except Exception:
    print("execption")
except KeyboardInterrupt:
        print("Data logging stopped.")
finally:
    log_file.close()
