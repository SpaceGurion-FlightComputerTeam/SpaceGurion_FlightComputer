import serial
import time

PORT = 'COM5'
BAUD_RATE = 230400

def get_next_serial_line(ser):
    """
    Reads the next available line from an open serial port object.
    Returns the line as a string, or None if no data received.
    Handles decoding errors gracefully.
    """
    try:
        line = ser.readline()  # Reads bytes until newline (\n)
        line = line.decode('utf-8', errors='ignore').strip()
        return line if line else None
    except serial.SerialException as e:
        print(f"[!] Serial error: {e}")
        return None
    
def serial_line_generator(timeout=1):
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=timeout)
        print(f"[✓] Connected to {PORT} at {BAUD_RATE} baud.")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    yield line
            else:
                print("[!] No data received. Waiting...")
                yield None
            time.sleep(0.1)


    # except serial.SerialException as e:
    #     print(f"[!] Serial error: {e}")
    except KeyboardInterrupt:
        print("\n[✓] Exiting on user request.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("[✓] Serial port closed.")

