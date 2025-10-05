#define L0m 11
#define L0p 10
#define port A0

void setup() 
{
  Serial.begin(115200);
}

void loop() {
  if ((digitalRead(L0m) == 1) && (digitalRead(L0p) == 1))
  {
    Serial.println("!");
  }
  else
  {
    int sensorValue = analogRead(port);
    
    Serial.println(sensorValue);
  }
  delay(1000);
}
