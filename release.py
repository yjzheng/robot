import time
import PCA9685_MG996R
# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685_MG996R.PCA9685_MG996R(PCA9685_MG996R.PCA9685_ADDRESS)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# MG996R TEST RESULT : 400 us ~ 2722 us
#define FREQUENCY           50
frequency = 50
# 600 us = 0 degree
# 1600 us = 90 degree
# 2600 us = 180 degree

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)
time.sleep(0.5)
for i in range(16):
    pwm.set_pwm(i, 0, 0)
time.sleep(0.5)
pwm.set_all_pwm(0,0)
time.sleep(0.5)
pwm.set_all_pwm(0,0)
time.sleep(0.5)
