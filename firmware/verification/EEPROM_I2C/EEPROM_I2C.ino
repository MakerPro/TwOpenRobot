/* 
  *  Use the I2C bus with EEPROM 24LC64 
  *  Sketch:    eeprom.pde
  *  
  *  Author: hkhijhe
  *  Date: 01/10/2010
  * 
  *   
  */

  #include <Wire.h> //I2C library

  void i2c_eeprom_write_byte( int deviceaddress, unsigned int eeaddress, byte data ) {
    int rdata = data;
    if(eeaddress>255) deviceaddress++;    
    Wire.beginTransmission(deviceaddress);
    //Wire.write((int)(eeaddress >> 8)); // MSB
    Wire.write((int)(eeaddress & 0xFF)); // LSB
    Wire.write(rdata);
    Wire.endTransmission();
  }

  // WARNING: address is a page address, 6-bit end will wrap around
  // also, data can be maximum of about 30 bytes, because the Wire library has a buffer of 32 bytes
  void i2c_eeprom_write_page( int deviceaddress, unsigned int eeaddresspage, byte* data, byte length ) {
    Wire.beginTransmission(deviceaddress);
    //Wire.write((int)(eeaddresspage >> 8)); // MSB
    Wire.write((int)(eeaddresspage & 0xFF)); // LSB
    byte c;
    for ( c = 0; c < length; c++)
      Wire.write(data[c]);
    Wire.endTransmission();
  }

  byte i2c_eeprom_read_byte( int deviceaddress, unsigned int eeaddress ) {
    byte rdata = 0xFF;
    if(eeaddress>255) deviceaddress++;
    Wire.beginTransmission(deviceaddress);
    //Wire.write((int)(eeaddress >> 8)); // MSB
    Wire.write((int)(eeaddress & 0xFF)); // LSB
    Wire.endTransmission(0);
    Wire.requestFrom(deviceaddress,1);
    while (Wire.available()){
      rdata = Wire.read();
      break;
    }
    return rdata;
  }

  // maybe let's not read more than 30 or 32 bytes at a time!
  void i2c_eeprom_read_buffer( int deviceaddress, unsigned int eeaddress, byte *buffer, int length ) {
    Wire.beginTransmission(deviceaddress);
    //Wire.write((int)(eeaddress >> 8)); // MSB
    Wire.write((int)(eeaddress & 0xFF)); // LSB
    Wire.endTransmission(0);
    Wire.requestFrom(deviceaddress,length);
    int c = 0;
    for ( c = 0; c < length; c++ )
      while(Wire.available()) {
        buffer[c] = Wire.read();
        break;
      }
  }

  char somedata[] = "012345678901234"; // data to write // the max size can only 15 byte

  void setup() 
  {
    Wire.begin(0x50); // initialise the connection
    Serial.begin(9600);
    //i2c_eeprom_write_page(0x50, 0, (byte *)somedata, sizeof(somedata)); // write to EEPROM 

    //delay(10); //add a small delay

    Serial.println("Memory written");
  }

  // this example verify at PLEN2 home make board V2 with i2c address fix to 0x50 A2=0
  void loop() 
  {
    int addr=0; //first address
    byte data = '0';
    delay(5000);
    byte b='0';
    int i;
    
    for(i=0;i<512;i++)
    {
      
      //i2c_eeprom_write_byte(0x50,addr,data);
      i2c_eeprom_write_byte(0x50,i,i%10+0x30);
      delay(20);
      
      //b = i2c_eeprom_read_byte(0x50, addr); //access an address from the memory
      b = i2c_eeprom_read_byte(0x50, i); //access an address from the memory
      delay(20);
      Serial.print((char)b); //print content to serial port
      //addr++; //increase address
      //data++;

    }
    Serial.println(" ");
    delay(2000);

  }
