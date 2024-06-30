import imu
import time
import numpy as np

class imuData:
    def __init__(self):
        self.imu = imu.IMU('/dev/ttyUSB0', 1250000)
   #     self.logFile = open("log.txt", "w")
        self.LastPosition = (0.0, 0.0, 0.0)
        self.lastSpeed = (0.0, 0.0, 0.0)
        self.rawGyro = []
        self.rawAccel = []
        self.orientation = np.array([1.0, 0.0, 0.0, 0.0])  # Quaternion representing orientation
        self.LastTime = time.time()

        


    def collectData(self, lastTime):
        currentTime = time.time()
        deltaTime = currentTime - lastTime

        # Retrieve gyro and accelerometer data
        gyroX = self.imu.gyro_axis_x
        gyroY = self.imu.gyro_axis_y
        gyroZ = self.imu.gyro_axis_z
        self.rawGyro = [gyroX, gyroY, gyroZ]

        accelX = self.imu.accelerometer_axis_x
        accelY = self.imu.accelerometer_axis_y
        accelZ = self.imu.accelerometer_axis_z
        self.rawAccel = [accelX, accelY, accelZ]

        # Update orientation using gyroscope data (simplified, assuming small angles)
        gyroVector = np.array([gyroX, gyroY, gyroZ]) * deltaTime
        self.orientation = self.updateOrientation(self.orientation, gyroVector)

        # Rotate accelerometer data to align with the global frame
        accelVector = np.array([accelX, accelY, accelZ])
        accelGlobal = self.rotateVector(self.orientation, accelVector)

        # Update speed using global accelerometer data
        speedX = self.lastSpeed[0] + accelGlobal[0] * deltaTime
        speedY = self.lastSpeed[1] + accelGlobal[1] * deltaTime
        speedZ = self.lastSpeed[2] + accelGlobal[2] * deltaTime

        # Update position using speed data
        positionX = self.LastPosition[0] + self.lastSpeed[0] * deltaTime + 0.5 * accelGlobal[0] * (deltaTime ** 2)
        positionY = self.LastPosition[1] + self.lastSpeed[1] * deltaTime + 0.5 * accelGlobal[1] * (deltaTime ** 2)
        positionZ = self.LastPosition[2] + self.lastSpeed[2] * deltaTime + 0.5 * accelGlobal[2] * (deltaTime ** 2)

        # Update last speed and position
        self.lastSpeed = (speedX, speedY, speedZ)
        self.LastPosition = (positionX, positionY, positionZ)


        # Return the current time for the next iteration
        return currentTime


    def updateOrientation(self, orientation, gyroVector):
        # Update the orientation quaternion based on the gyroscope vector
        # This is a simplified version and may require a more robust approach in practice
        deltaQuat = np.array([0, gyroVector[0], gyroVector[1], gyroVector[2]])
        orientation += 0.5 * self.quaternionProduct(orientation, deltaQuat)
        orientation = orientation / np.linalg.norm(orientation)  # Normalize quaternion
        return orientation

    def rotateVector(self, orientation, vector):
        # Rotate a vector by the given quaternion
        q = orientation
        v = np.array([0, vector[0], vector[1], vector[2]])
        q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
        return self.quaternionProduct(self.quaternionProduct(q, v), q_conj)[1:]

    def quaternionProduct(self, q1, q2):
        # Calculate the product of two quaternions
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])
    

    def read(self):
        self.LastTime = time.time()  # Initialize lastTime
 #       self.writeHeader()
        counter = 0
        try:
            self.imu.get()
            self.LastTime = self.collectData(self.LastTime)  # Update lastTime with the return value
            return self.LastPosition, self.lastSpeed , self.rawAccel, self.rawGyro
        except KeyboardInterrupt:
            self.close()

    
        
    
    def close(self):
        self.imu.stop()
        self.logFile.close()

if __name__ == "__main__":
    imuData = imuData()
    
    while True:
        print(imuData.read()[0])
        