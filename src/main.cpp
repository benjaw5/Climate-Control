#include <Arduino.h>
#include <Wire.h>
#include "SparkFun_Si7021_Breakout_Library.h"
#include "SparkFun_ENS160.h"
#include <SPI.h>
#include <HttpClient.h>
#include <WiFi.h>
#include <inttypes.h>
#include <stdio.h>
#include "esp_system.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs.h"
#include "nvs_flash.h"



char ssid[50]; // your network SSID (name)
char pass[50]; // your network password (use for WPA, or use
// as key for WEP)
// Name of the server we want to connect to
const char kHostname[] = "worldtimeapi.org";
// Path to download (this is the bit after the hostname in the URL
// that you want to download
const char kPath[] = "/api/timezone/Europe/London.txt";
// Number of milliseconds to wait without receiving any data before we give up
const int kNetworkTimeout = 30 * 1000;
// Number of milliseconds to wait if no data is available before trying again
const int kNetworkDelay = 1000;
void nvs_access() {
  // Initialize NVS
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES ||
    err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    // NVS partition was truncated and needs to be erased
    // Retry nvs_flash_init
    ESP_ERROR_CHECK(nvs_flash_erase());
    err = nvs_flash_init();
  }
    ESP_ERROR_CHECK(err);
    // Open
    Serial.printf("\n");
    Serial.printf("Opening Non-Volatile Storage (NVS) handle... ");
    nvs_handle_t my_handle;
  err = nvs_open("storage", NVS_READWRITE, &my_handle);
  if (err != ESP_OK) {
    Serial.printf("Error (%s) opening NVS handle!\n", esp_err_to_name(err));
  } else {
    Serial.printf("Done\n");
    Serial.printf("Retrieving SSID/PASSWD\n");
    size_t ssid_len;
    size_t pass_len;
    nvs_get_str(my_handle, "ssid", NULL, &ssid_len);
    nvs_get_str(my_handle, "pass", NULL, &pass_len);
    err = nvs_get_str(my_handle, "ssid", ssid, &ssid_len);
    err |= nvs_get_str(my_handle, "pass", pass, &pass_len);
    switch (err) {
      case ESP_OK:
        Serial.printf("Done\n");
        //Serial.printf("SSID = %s\n", ssid);
        //Serial.printf("PASSWD = %s\n", pass);
        break;
      case ESP_ERR_NVS_NOT_FOUND:
        Serial.printf("The value is not initialized yet!\n");
        break;
      default:
        Serial.printf("Error (%s) reading!\n", esp_err_to_name(err));
      }
  }
  // Close
  nvs_close(my_handle);
}

SI7021 sensor;
SparkFun_ENS160 AirQuality;
// SPIClass spi(HSPI);

int chipSelect = 2; 
int ensStatus = 0; 

void setup() {
  Serial.begin(9600);
  Wire.begin();
  nvs_access();
  Serial.printf(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.println("MAC address: ");
  Serial.println(WiFi.macAddress());
  sensor.begin();
  // pinMode(chipSelect, OUTPUT);
	// digitalWrite(chipSelect, HIGH);
  
  // spi.begin(25,26,27,chipSelect);
  if(!AirQuality.begin()){
    Serial.println("Could not communicate with the ENS160, check wiring.");
		// while(1);
  }

  if( AirQuality.setOperatingMode(SFE_ENS160_RESET) )
		Serial.println("Ready.");

  delay(100);

  AirQuality.setOperatingMode(SFE_ENS160_STANDARD);
  Serial.print("Operating Mode: ");
	Serial.println(AirQuality.getOperatingMode());

  ensStatus = AirQuality.getFlags();
	Serial.print("Gas Sensor Status Flag (0 - Standard, 1 - Warm up, 2 - Initial Start Up): ");
	Serial.println(ensStatus);

}

void loop() {
  float humidity = sensor.getRH();
  float temp = sensor.getTempF();

  Serial.println(humidity);
  Serial.println(temp);
  int AQI;
  int TVOC;
  int CO2;
  if( AirQuality.checkDataStatus() )
	{
    AQI = AirQuality.getAQI();
		Serial.print("Air Quality Index (1-5) : ");
		Serial.println(AirQuality.getAQI());

    TVOC = AirQuality.getTVOC();
		Serial.print("Total Volatile Organic Compounds: ");
		Serial.print(AirQuality.getTVOC());
		Serial.println("ppb");

    CO2 = AirQuality.getECO2();
		Serial.print("CO2 concentration: ");
		Serial.print(AirQuality.getECO2());
		Serial.println("ppm");

		Serial.println();
	}
  sleep(2);

  int err = 0;
  WiFiClient c;
  HttpClient http(c);
//   err = http.get(kHostname, kPath);
//   err = http.get("184.169.242.238", 5000, "/?var=10", NULL);
  std::string tempString = "/data/?temp=" + std::to_string(temp) + "&humid=" + std::to_string(humidity) 
  + "&aqi=" + std::to_string(AQI) + "&tvoc=" + std::to_string(TVOC)
  + "&co2=" + std::to_string(CO2);
  //err = http.get("184.169.242.238", 5000, tempString.c_str(), NULL);
  err |= http.get("184.169.235.42", 5000, tempString.c_str(), NULL);
  if (err == 0) {
    Serial.println("startedRequest ok");
    err = http.responseStatusCode();
    if (err >= 0) {
      Serial.print("Got status code: ");
      Serial.println(err);
      // Usually you'd check that the response code is 200 or a
      // similar "success" code (200-299) before carrying on,
      // but we'll print out whatever response we get
      err = http.skipResponseHeaders();
      if (err >= 0) {
        int bodyLen = http.contentLength();
        Serial.print("Content length is: ");
        Serial.println(bodyLen);
        Serial.println();
        Serial.println("Body returned follows:");
        // Now we've got to the body, so we can print it out
        unsigned long timeoutStart = millis();
        char c;
        // Whilst we haven't timed out & haven't reached the end of the body
        while ((http.connected() || http.available()) &&
          ((millis() - timeoutStart) < kNetworkTimeout)) {
          if (http.available()) {
          c = http.read();
            // Print out this character
            Serial.print(c);
            bodyLen--;
            // We read something, reset the timeout counter
            timeoutStart = millis();
          } else {
            // We haven't got any data, so let's pause to allow some to
            // arrive
            delay(kNetworkDelay);
          }
        }
      } else {
        Serial.print("Failed to skip response headers: ");
        Serial.println(err);
      }
    } else {
      Serial.print("Getting response failed: ");
      Serial.println(err);
    }
  } else {
    Serial.print("Connect failed: ");
    Serial.println(err);
  }
  http.stop();
}
