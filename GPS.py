from ublox_gps import UbloxGps
import serial

def run():
    try:
        port = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)
        gps = UbloxGps(port)
        
        print("Listening for UBX Messages.")

        while True:
            try:
                coords = gps.geo_coords()
                if coords is not None:
                    print(coords.lon, coords.lat)
                else:
                    print("No GPS fix available.")
            except (ValueError, IOError) as err:
                print(err)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    finally:
        if 'port' in locals() and port.is_open:
            port.close()

if __name__ == '__main__':
    run()

