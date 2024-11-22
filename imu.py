import serial
import numpy as np

PACKET_SIZE = 36
ACCELERATION_FACTOR = (2**15)
GYRO_FACTOR = (2**12)
TWOS_COMPLIMENT_FACTOR = (1 << 23)
TEMPERATURE_FACTOR = 10

def values_adapt(value, factor):
    if value & TWOS_COMPLIMENT_FACTOR:
        value = 0xFFFFFF - value + 1
        value = np.int32(-value)
    return value / factor

class MainStatus:
    def __init__(self, val):
        self.set(val)

    def set(self, val):
        self.val = val
        self.high_g_sensor_in_all_axes = bool(val & (1 << 4))
        self.acc_x_ok = not bool(val & (1 << 5))
        self.acc_y_ok = not bool(val & (1 << 6))
        self.acc_z_ok = not bool(val & (1 << 7))
        self.gyro_x_ok = not bool(val & (1 << 9))
        self.gyro_y_ok = not bool(val & (1 << 10))
        self.gyro_z_ok = not bool(val & (1 << 11))
        self.sync_signal_exists = not bool(val & (1 << 12))
        self.normal_mode = not bool(val & 0x6000)
        self.BIT_mode = bool(val & (1 << 13))
        self.fault_mode = bool(val & (1 << 13)) and bool(val & (1 << 14))
        self.gyro_ranges_ok = not bool(val & (1 << 15))

class IMU:
    def __init__(self, com_port, baudrate):
        self.ser = serial.Serial(com_port, baudrate=baudrate)
        self.main_status = MainStatus(0)

    def get(self):
        packet = []
        while True:
            start_byte = self.ser.read()
            if start_byte == b'\x24':
                packet.append(start_byte)
                for _ in range(1, PACKET_SIZE):
                    packet.append(self.ser.read())
                if packet[PACKET_SIZE - 1] == b'\x23':
                    self.parse_packet(packet)
                    self.sensor_values_adaptions()
                    return self
                else:
                    packet = []
            else:
                packet = []

    def parse_packet(self, packet):
        packet_int = [int.from_bytes(x, byteorder='little') for x in packet]
        self.main_status.set(packet_int[5] + (packet_int[6] << 8))
        self.gyro_axis_x = packet_int[8] + (packet_int[9] << 8) + (packet_int[10] << 16)
        self.gyro_axis_y = packet_int[11] + (packet_int[12] << 8) + (packet_int[13] << 16)
        self.gyro_axis_z = packet_int[14] + (packet_int[15] << 8) + (packet_int[16] << 16)
        self.accelerometer_axis_x = packet_int[17] + (packet_int[18] << 8) + (packet_int[19] << 16)
        self.accelerometer_axis_y = packet_int[20] + (packet_int[21] << 8) + (packet_int[22] << 16)
        self.accelerometer_axis_z = packet_int[23] + (packet_int[24] << 8) + (packet_int[25] << 16)
        self.accelerometer_axis_x_high_g = packet_int[26] + (packet_int[27] << 8) + (packet_int[28] << 16)
        self.temperature = packet_int[29] + (packet_int[30] << 8)
        self.sw_version = packet_int[31]
        self.counter = packet_int[32]
        self.crc = packet_int[33] + (packet_int[34] << 8)

    def sensor_values_adaptions(self):
        self.gyro_axis_x = values_adapt(self.gyro_axis_x, GYRO_FACTOR)
        self.gyro_axis_y = values_adapt(self.gyro_axis_y, GYRO_FACTOR)
        self.gyro_axis_z = values_adapt(self.gyro_axis_z, GYRO_FACTOR)
        self.accelerometer_axis_x = values_adapt(self.accelerometer_axis_x, ACCELERATION_FACTOR)
        self.accelerometer_axis_y = values_adapt(self.accelerometer_axis_y, ACCELERATION_FACTOR)
        self.accelerometer_axis_z = values_adapt(self.accelerometer_axis_z, ACCELERATION_FACTOR) - 1
        self.accelerometer_axis_x_high_g = values_adapt(self.accelerometer_axis_x_high_g, ACCELERATION_FACTOR)
        self.temperature = self.temperature / TEMPERATURE_FACTOR
