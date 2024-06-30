import board
import busio
import adafruit_bmp280


class Barometer:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c)
        self.bmp280.sea_level_pressure = 1013.25
    def read(self):
        try:
            temperature = self.bmp280.temperature
            pressure = self.bmp280.pressure
            altitude = self.bmp280.altitude
            return temperature, pressure, altitude
        except Exception as e:
            print(f"Failed to read from BMP280 sensor: {e}")
            return None, None, None

if __name__ == "__main__":
    barometer = Barometer()
    while True:
        temperature, pressure, altitude = barometer.read()
        print(f"Temperature: {temperature:.2f} C, Pressure: {pressure:.2f} hPa, Altitude: {altitude:.2f} m")
        