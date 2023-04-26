#include <Arduino.h>
#include <Wire.h>

// DHT library
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#include "Adafruit_SGP30.h"
#include "Adafruit_CCS811.h"

// DHT11 define
#define DHTPIN 19
#define DHTTYPE DHT11

DHT_Unified dht(DHTPIN, DHTTYPE);

// Mic define
#define MicPIN 5

// SGP define
Adafruit_SGP30 sgp;

// CCS define
Adafruit_CCS811 ccs;

uint32_t getAbsoluteHumidity(float temperature, float humidity) 
{
    // approximation formula from Sensirion SGP30 Driver Integration chapter 3.15
    const float absoluteHumidity = 216.7f * ((humidity / 100.0f) * 6.112f * exp((17.62f * temperature) / (243.12f + temperature)) / (273.15f + temperature)); // [g/m^3]
    const uint32_t absoluteHumidityScaled = static_cast<uint32_t>(1000.0f * absoluteHumidity); // [mg/m^3]
    return absoluteHumidityScaled;
}

// multi scheduler params
int mic_samp_micros = 100;
int dht_samp_micros = 2000000;
int sgp_samp_micros = 500000;
int ccs_samp_micros = 200000;

// moving avg params
float alpha = 0.001;

void setup() 
{
  Serial.begin(9600);
  dht.begin();
  pinMode(21,INPUT);

  // SGP30 
  Serial.println("before sgp");
  while (! sgp.begin())
  {
    Serial.println("SGP30 not found :(");
  }
  Serial.print("Found SGP30 serial #");
  Serial.print(sgp.serialnumber[0], HEX);
  Serial.print(sgp.serialnumber[1], HEX);
  Serial.println(sgp.serialnumber[2], HEX);

  Serial.println("before ccs");
  // ccs sensor
  while(!ccs.begin())
  {
    Serial.println("Failed to start CCS! Please check your wiring.");
  }
  Serial.println("after ccs");

  //calibrate CCS sensor
  while(!ccs.available());
  float temp = ccs.calculateTemperature();
  ccs.setTempOffset(temp - 25.0);

}

long mic_next = 0;
long dht_next = 0;
long sgp_next = 0;
long ccs_next = 0;

float mic_read = 0;
int mic_count = 0;

int sgp_count = 0;

void loop() 
{
  //Serial.println("------");
  
  long cur_time = micros();
  if (cur_time > mic_next)
  {
    mic_next = cur_time + mic_samp_micros;
    mic_read = alpha*digitalRead(MicPIN) + (1-alpha)*mic_read;
    mic_count++;
    if(mic_count >99)
    {
      /*Serial.print(cur_time);
      Serial.print(",");
      Serial.println(mic_read);*/
      mic_count = 0;
    }
  }

  
  if (cur_time > dht_next)
  {
    dht_next = cur_time + dht_samp_micros;
    // DHT reading
    sensors_event_t event;
    dht.temperature().getEvent(&event);
    if (isnan(event.temperature))
    {
      Serial.println(F("Error reading temperature!"));
    }
    else
    {
      Serial.print(F("Temperature: "));
      Serial.print(event.temperature);
      Serial.println(F("°C"));
    }
    // Get humidity event and print its value.
    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity))
    {
      Serial.println(F("Error reading humidity!"));
    }
    else
    {
      Serial.print(F("Humidity: "));
      Serial.print(event.relative_humidity);
      Serial.println(F("%"));
    }
  }

  if (cur_time > sgp_next)
  {
    sgp_next = cur_time + sgp_samp_micros;
    if (!sgp.IAQmeasure())
    {
      Serial.println("Measurement failed");
      return;
    }
    Serial.print("TVOC ");
    Serial.print(sgp.TVOC);
    Serial.print(" ppb\t");
    Serial.print("eCO2 ");
    Serial.print(sgp.eCO2);
    Serial.println(" ppm");

    if (!sgp.IAQmeasureRaw())
    {
      Serial.println("Raw Measurement failed");
      return;
    }
    Serial.print("Raw H2 ");
    Serial.print(sgp.rawH2);
    Serial.print(" \t");
    Serial.print("Raw Ethanol ");
    Serial.print(sgp.rawEthanol);
    Serial.println("");

    sgp_count++;
    if (sgp_count == 30)
    {
      sgp_count = 0;

      uint16_t TVOC_base, eCO2_base;
      if (!sgp.getIAQBaseline(&eCO2_base, &TVOC_base))
      {
        Serial.println("Failed to get baseline readings");
        return;
      }
      Serial.print("****Baseline values: eCO2: 0x");
      Serial.print(eCO2_base, HEX);
      Serial.print(" & TVOC: 0x");
      Serial.println(TVOC_base, HEX);
    }
  }

  /*if (cur_time > ccs_next)
  {
    ccs_next = cur_time + ccs_samp_micros;
    if (ccs.available())
    {
      float temp = ccs.calculateTemperature();
      if (!ccs.readData())
      {
        Serial.print("eCO2: ");
        float eCO2 = ccs.geteCO2();
        Serial.print(eCO2);

        Serial.print(" ppm, TVOC: ");
        float TVOC = ccs.getTVOC();
        Serial.print(TVOC);

        Serial.print(" ppb   Temp:");
        Serial.println(temp);
      }
      else
      {
        Serial.println("ERROR!");
        while (1);
      }
    }
  }*/

}