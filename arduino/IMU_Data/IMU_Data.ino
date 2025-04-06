#include <Wire.h>
#include "ICM_20948.h"

// I2C implementation
ICM_20948_I2C myICM;

// Define serial output rate (Hz)
const int SERIAL_HZ = 50;
unsigned long lastSample = 0;
const unsigned long sampleDelay = 1000 / SERIAL_HZ;

void setup() {
  Serial.begin(115200);
  while (!Serial) {
    ; // Wait for serial port to connect
  }

  Wire.begin();
  Wire.setClock(400000); // 400kHz I2C clock

  delay(100);
  
  bool initialized = false;
  while (!initialized) {
    // Use address 1 (0x69) instead of 0 (0x68)
    myICM.begin(Wire, 1);
    
    if (myICM.status != ICM_20948_Stat_Ok) {
      Serial.println("ICM-20948 not detected on I2C bus.");
      delay(500);
    } else {
      initialized = true;
      Serial.println("ICM-20948 initialized successfully!");
    }
  }

  // Set up digital low-pass filter configuration
  ICM_20948_dlpcfg_t dlpcfg;
  dlpcfg.a = acc_d11bw5_n17bw;  
  dlpcfg.g = gyr_d11bw6_n17bw8;  
  myICM.setDLPFcfg((ICM_20948_Internal_Acc | ICM_20948_Internal_Gyr), dlpcfg);

  // Set gyroscope full-scale range
  ICM_20948_fss_t myFSS;
  myFSS.a = gpm16;   // ±16g (for high acceleration during launch)
  myFSS.g = dps2000; // ±2000°/s (for rapid rocket spins)
  myICM.setFullScale((ICM_20948_Internal_Acc | ICM_20948_Internal_Gyr), myFSS);

  // Optional: Set up sample rate divider
  ICM_20948_smplrt_t mySmplrt;
  mySmplrt.a = 4; // 220Hz for accelerometer
  mySmplrt.g = 4; // 220Hz for gyroscope
  myICM.setSampleRate((ICM_20948_Internal_Acc | ICM_20948_Internal_Gyr), mySmplrt);

  // Enable FIFO for smoother data handling
  myICM.enableFIFO(true);
  
  Serial.println("Setup complete");
}

void loop() {
  // Check if it's time to read a sample
  if ((millis() - lastSample) >= sampleDelay) {
    lastSample = millis();
    
    // Read sensor data
    if (myICM.dataReady()) {
      myICM.getAGMT();

      // Format data as JSON for easy parsing on the web side
      Serial.print("{");
      
      // Accelerometer data in g
      Serial.print("\"ax\":");
      Serial.print(myICM.accX() / 1000.0, 3);
      Serial.print(",\"ay\":");
      Serial.print(myICM.accY() / 1000.0, 3);
      Serial.print(",\"az\":");
      Serial.print(myICM.accZ() / 1000.0, 3);
      
      // Gyroscope data in degrees/second
      Serial.print(",\"gx\":");
      Serial.print(myICM.gyrX(), 3);
      Serial.print(",\"gy\":");
      Serial.print(myICM.gyrY(), 3);
      Serial.print(",\"gz\":");
      Serial.print(myICM.gyrZ(), 3);
      
      // Magnetometer data in μT
      Serial.print(",\"mx\":");
      Serial.print(myICM.magX(), 3);
      Serial.print(",\"my\":");
      Serial.print(myICM.magY(), 3);
      Serial.print(",\"mz\":");
      Serial.print(myICM.magZ(), 3);
      
      // Add timestamp
      Serial.print(",\"time\":");
      Serial.print(millis());
      
      Serial.println("}");
    }

    
  }
}