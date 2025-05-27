

/*

*/
#include "helper.h"
  Adafruit_BMP280 bmp;
  bool BARSetup() {
    if (!bmp.begin()) {
      Serial.println("❌ Could not find BMP280 sensor. Check wiring or address.");
      return false;
    }

    bmp.setSampling(Adafruit_BMP280::MODE_FORCED,    //The sensor only measures once when you explicitly ask it to
                    Adafruit_BMP280::SAMPLING_X2,    //Take 2 temp samples and average them
                    Adafruit_BMP280::SAMPLING_X16,   //Take 16 pressure samples
                    Adafruit_BMP280::FILTER_X16,     //for smoothing fast changes (e.g. sudden vibration or movement).
                    Adafruit_BMP280::STANDBY_MS_500); //between measurements in normal mode, 500ms

    Serial.println("✅ BMP280 initialized.");
    return true;
  }

  bool readSensor(float &temperature, float &pressure, float &altitude) {
    if (bmp.takeForcedMeasurement()) {
      temperature = bmp.readTemperature();
      pressure = bmp.readPressure();
      altitude = bmp.readAltitude(SEA_LEVEL_PRESSURE_HPA);
      return true;
    } else {
      return false;
    }
  }

  String getFormattedData() {
    float temp, press, alt;
    if (readSensor(temp, press, alt)) {
      return String(temp, 2) + "," + String(press, 0) + "," + String(alt, 2);
    } else {
      Serial.println("BMP280 measurement failed!");
      return "N/A,N/A,N/A";
    }
  }



