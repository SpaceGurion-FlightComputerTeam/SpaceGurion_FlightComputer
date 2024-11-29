# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Simple GPS module demonstration.
# This code waits for a GPS fix and prints location details every second.
import time
import board
import busio
import adafruit_gps

# Create a serial connection for the GPS module using default speed and a slightly higher timeout.
# GPS modules typically update once a second.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
# For a computer, use the pyserial library for UART access.
import serial
uart = serial.Serial("/dev/serial0", baudrate=9600, timeout=10)

# If using I2C, you can create an I2C interface to talk to using default pins.
# i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c, debug=False)  # Use I2C interface

# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and PMTK_220_SET_NMEA_UPDATERATE.
# You can adjust the GPS module's behavior using these commands.
# More details can be found in the datasheet: https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf
# Explanation for each gps.send_command() parameter:
# PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
# This command sets the NMEA output sentences to GGA, RMC, VTG, GSA, GSV, and GLL.
# The parameters are as follows:
# - $PMTK314: Command header
# - 0: GGA sentence (Global Positioning System Fix Data) - Disable
# - 1: RMC sentence (Recommended Minimum Specific GNSS Data) - Enable
# - 0: VTG sentence (Course Over Ground and Ground Speed) - Disable
# - 1: GSA sentence (GNSS DOP and Active Satellites) - Enable
# - 0: GSV sentence (GNSS Satellites in View) - Disable
# - 0: GLL sentence (Geographic Position - Latitude/Longitude) - Disable
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
# - 0: Reserved
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

# Set update rate to once a second (1hz), which is typical.
gps.send_command(b"PMTK220,1000")

# Main loop runs forever, printing the location details every second.
last_print = time.monotonic()
while True:
    # Make sure to call gps.update() every loop iteration and at least twice
    # as fast as data comes from the GPS unit (usually every second).
    # This returns a bool that's true if it parsed new data.
    gps.update()

    # Every second, print out current location details if there's a fix.
    current = time.monotonic()
    if current - last_print >= 1.0:
        last_print = current
        if not gps.has_fix:
            # Try again if we don't have a fix yet.
            print("Waiting for fix...")
            continue

        # We have a fix! (gps.has_fix is true)
        # Print out details about the fix like location, date, etc.
        print("=" * 40)  # Print a separator line.
        print(
            "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
                gps.timestamp_utc.tm_mon,  # Grab parts of the time from the struct_time object.
                gps.timestamp_utc.tm_mday,
                gps.timestamp_utc.tm_year,
                gps.timestamp_utc.tm_hour,
                gps.timestamp_utc.tm_min,
                gps.timestamp_utc.tm_sec,
            )
        )
        print("Latitude: {:.6f} degrees".format(gps.latitude))
        print("Longitude: {:.6f} degrees".format(gps.longitude))
        print(
            "Precise Latitude: {:2.0f}{:2.4f} degrees".format(
                gps.latitude_degrees, gps.latitude_minutes
            )
        )
        print(
            "Precise Longitude: {:3.0f}{:2.4f} degrees".format(
                gps.longitude_degrees, gps.longitude_minutes
            )
        )
        print("Fix quality: {}".format(gps.fix_quality))

        # Check if additional attributes are not None before printing them.
        if gps.satellites is not None:
            print("# satellites: {}".format(gps.satellites))
        if gps.altitude_m is not None:
            print("Altitude: {} meters".format(gps.altitude_m))
        if gps.speed_knots is not None:
            print("Speed: {} knots".format(gps.speed_knots))
        if gps.track_angle_deg is not None:
            print("Track angle: {} degrees".format(gps.track_angle_deg))
        if gps.horizontal_dilution is not None:
            print("Horizontal dilution: {}".format(gps.horizontal_dilution))
        if gps.height_geoid is not None:
            print("Height geoid: {} meters".format(gps.height_geoid))
