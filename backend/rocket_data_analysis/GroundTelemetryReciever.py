import serial
import time

PORT = 'COM5'
BAUD_RATE = 9600

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
            time.sleep(0.1)


    # except serial.SerialException as e:
    #     print(f"[!] Serial error: {e}")
    except KeyboardInterrupt:
        print("\n[✓] Exiting on user request.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("[✓] Serial port closed.")

