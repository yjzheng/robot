// Library Manager add Adafruit PWM Servo Driver Libaray
// https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library
// https://github.com/adafruit/Adafruit_BusIO/tree/master
//
#include <Wire.h>
#include <Adafruit_I2CDevice.h>

// REGISTER ADDRESSES
#define PCA9685_MODE1 0x00      /**< Mode Register 1 */
#define PCA9685_MODE2 0x01      /**< Mode Register 2 */
#define PCA9685_SUBADR1 0x02    /**< I2C-bus subaddress 1 */
#define PCA9685_SUBADR2 0x03    /**< I2C-bus subaddress 2 */
#define PCA9685_SUBADR3 0x04    /**< I2C-bus subaddress 3 */
#define PCA9685_ALLCALLADR 0x05 /**< LED All Call I2C-bus address */
#define PCA9685_LED0_ON_L 0x06  /**< LED0 on tick, low byte*/
#define PCA9685_LED0_ON_H 0x07  /**< LED0 on tick, high byte*/
#define PCA9685_LED0_OFF_L 0x08 /**< LED0 off tick, low byte */
#define PCA9685_LED0_OFF_H 0x09 /**< LED0 off tick, high byte */
// etc all 16:  LED15_OFF_H 0x45
#define PCA9685_ALLLED_ON_L 0xFA  /**< load all the LEDn_ON registers, low */
#define PCA9685_ALLLED_ON_H 0xFB  /**< load all the LEDn_ON registers, high */
#define PCA9685_ALLLED_OFF_L 0xFC /**< load all the LEDn_OFF registers, low */
#define PCA9685_ALLLED_OFF_H 0xFD /**< load all the LEDn_OFF registers,high */
#define PCA9685_PRESCALE 0xFE     /**< Prescaler for PWM output frequency */
#define PCA9685_TESTMODE 0xFF     /**< defines the test mode to be entered */

// MODE1 bits
#define MODE1_ALLCAL 0x01  /**< respond to LED All Call I2C-bus address */
#define MODE1_SUB3 0x02    /**< respond to I2C-bus subaddress 3 */
#define MODE1_SUB2 0x04    /**< respond to I2C-bus subaddress 2 */
#define MODE1_SUB1 0x08    /**< respond to I2C-bus subaddress 1 */
#define MODE1_SLEEP 0x10   /**< Low power mode. Oscillator off */
#define MODE1_AI 0x20      /**< Auto-Increment enabled */
#define MODE1_EXTCLK 0x40  /**< Use EXTCLK pin clock */
#define MODE1_RESTART 0x80 /**< Restart enabled */
// MODE2 bits
#define MODE2_OUTNE_0 0x01 /**< Active LOW output enable input */
#define MODE2_OUTNE_1 0x02 /**< Active LOW output enable input - high impedience */
#define MODE2_OUTDRV 0x04 /**< totem pole structure vs open-drain */
#define MODE2_OCH 0x08    /**< Outputs change on ACK vs STOP */
#define MODE2_INVRT 0x10  /**< Output logic state inverted */

#define PCA9685_I2C_ADDRESS 0x40      /**< Default PCA9685 I2C Slave Address */
#define FREQUENCY_OSCILLATOR 25000000 /**< Int. osc. frequency in datasheet */

#define PCA9685_PRESCALE_MIN 3   /**< minimum prescale value */
#define PCA9685_PRESCALE_MAX 255 /**< maximum prescale value */

//uint8_t _i2caddr;
TwoWire *_i2c;
Adafruit_I2CDevice *i2c_dev = NULL;

uint8_t read8(uint8_t addr) {
  uint8_t buffer[1] = {addr};
  i2c_dev->write_then_read(buffer, 1, buffer, 1);
  return buffer[0];
}

void write8(uint8_t addr, uint8_t d) {
  uint8_t buffer[2] = {addr, d};
  i2c_dev->write(buffer, 2);
}
uint32_t _oscillator_freq;

// called this way, it uses the default address 0x40
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  150 // This is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // This is the 'maximum' pulse length count (out of 4096)
#define USMIN  600 // This is the rounded 'minimum' microsecond length based on the minimum pulse of 150
#define USMAX  2400 // This is the rounded 'maximum' microsecond length based on the maximum pulse of 600
#define SERVO_FREQ 50 // Analog servos run at ~50 Hz updates

uint8_t prescale;
// our servo # counter
uint8_t servonum = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("8 channel Servo test!");

  i2c_dev = new Adafruit_I2CDevice(PCA9685_I2C_ADDRESS);
  bool flag = i2c_dev->begin();
  Serial.println((int)flag);
  write8(PCA9685_MODE1, MODE1_RESTART);
  delay(10);

  _oscillator_freq = 27000000;

  prescale = 131; // ((_oscillator_freq / (freq * 4096.0)) + 0.5) - 1;
  uint8_t oldmode = read8(PCA9685_MODE1);
  uint8_t newmode = (oldmode & ~MODE1_RESTART) | MODE1_SLEEP; // sleep
  write8(PCA9685_MODE1, newmode);                             // go to sleep
  write8(PCA9685_PRESCALE, prescale); // set the prescaler
  write8(PCA9685_MODE1, oldmode);
  delay(5);
  // This sets the MODE1 register to turn on auto increment.
  write8(PCA9685_MODE1, oldmode | MODE1_RESTART | MODE1_AI);

  delay(10);
}

uint8_t setPWM(uint8_t num, uint16_t on, uint16_t off) {
  uint8_t buffer[5];
  buffer[0] = PCA9685_LED0_ON_L + 4 * num;
  buffer[1] = on;
  buffer[2] = on >> 8;
  buffer[3] = off;
  buffer[4] = off >> 8;

  if (i2c_dev->write(buffer, 5)) {
    return 0;
  } else {
    return 1;
  }
}

uint8_t readPrescale(void) {
  return read8(PCA9685_PRESCALE);
}

void writeMicroseconds(uint8_t num, uint16_t Microseconds) {

  double pulse = Microseconds;
  double pulselength;
  pulselength = 1000000; // 1,000,000 us per second

  // Read prescale
  //uint16_t prescale2 = readPrescale();
  //prescale = 131;

  // Calculate the pulse for PWM based on Equation 1 from the datasheet section
  // 7.3.5
  pulselength *= prescale + 1;
  pulselength /= _oscillator_freq;

  pulse /= pulselength;

  setPWM(num, 0, pulse);
}

void loop() {
  // Drive each servo one at a time using setPWM()
  Serial.println(servonum);
  for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
    setPWM(servonum, 0, pulselen);
  }

  delay(500);
  for (uint16_t pulselen = SERVOMAX; pulselen > SERVOMIN; pulselen--) {
    setPWM(servonum, 0, pulselen);
  }

  delay(500);

  for (uint16_t microsec = USMIN; microsec < USMAX; microsec++) {
    writeMicroseconds(servonum, microsec);
  }

  delay(500);
  for (uint16_t microsec = USMAX; microsec > USMIN; microsec--) {
    writeMicroseconds(servonum, microsec);
  }

  delay(500);

  servonum++;
  if (servonum > 7) servonum = 0; // Testing the first 8 servo channels
}
