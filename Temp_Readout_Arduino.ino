#include <Arduino.h>

// Series Pins
#define ana_rel_00 A0
#define ana_rel_01 A1
#define ana_rel_10 A2
#define ana_rel_11 A3

// Bridge Pins
#define ana_abs_0 A8
#define ana_abs_1 A9

const float range = 1023.0f; // 10 bit arduino uno ADC (resolution)
int tot_avg_runs = 500.0f; // total number of average iterations
float shock_const = 5035.3f; // Determined by parallel diode with 10:1 res ratio
float gain = 51.93f; // Determined by diff amp resistor value
float initial_volt0 = 0.0f;
float initial_volt1 = 0.0f;


struct Temp {
  float temp_abs;
  float temp_rel;
};

// Read Voltage Function
float read_voltage(const int pin){
  float val = analogRead(pin);
  float volt = (val * 5.0f) / range;

  return volt;
}
// Take Average Voltage (for rel temp)
float avg_volt(const int pin0, const int pin1){
  float sum = 0.0f;
  float val = 0.0f;

  for(int i = 0; i < tot_avg_runs; i++){
    val = read_voltage(pin1) - read_voltage(pin0);
    sum += val;
    delay(5);
  }
  float avg = sum / tot_avg_runs;
  return avg;
}

Temp get_temps(float volt_initial, const int pin_rel0, const int pin_rel1, const int pin_abs, float baseline = 273.0f){
  Temp temp; 

  float volt_rel_0 = read_voltage(pin_rel0);
  float volt_rel_1 = read_voltage(pin_rel1);
  float volt_abs = read_voltage(pin_abs);

  float volt_rel = volt_rel_1 - volt_rel_0;
  temp.temp_rel = (volt_initial - volt_rel) * 100.0f;
  temp.temp_abs = ((shock_const * volt_abs)/gain) - baseline;

  return temp;
}

// Classic Setup Function
void setup() {
  Serial.begin(9600);
  initial_volt0 = avg_volt(ana_rel_00, ana_rel_01);
  initial_volt1 = avg_volt(ana_rel_10, ana_rel_11);
}
// Classic Loop Function
void loop() {
  Temp temp0 = get_temps(initial_volt0, ana_rel_00, ana_rel_01, ana_abs_0, 309.0f); // Change baseline (last argument)
  Temp temp1 = get_temps(initial_volt1, ana_rel_10, ana_rel_11, ana_abs_1, 303.0f); // CHange baseline (last argument)

  float temp_abs_0 = temp0.temp_abs;
  float temp_rel_0 = temp0.temp_rel;
  float temp_abs_1 = temp1.temp_abs;
  float temp_rel_1 = temp1.temp_rel;

  Serial.print(temp_abs_0);
  Serial.print(", ");
  Serial.print(temp_rel_0);
  Serial.print(", ");
  Serial.print(temp_abs_1);
  Serial.print(", ");
  Serial.println(temp_rel_1);

  delay(1000);
}
