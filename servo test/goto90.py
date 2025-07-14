#import os
#try:
#    os.remove("dt00.dat")
#except:
#    pass

import time
import PCA9685_MG996R
# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685_MG996R.PCA9685_MG996R(PCA9685_MG996R.PCA9685_ADDRESS)

# MG996R TEST RESULT : 400 us ~ 2722 us
#define FREQUENCY           50
frequency = 50

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)

channel = 0
print("move to angle 0")
pwm.rotate_to_angle( channel, 0)
time.sleep(1)
print("move to angle 90")
pwm.rotate_to_angle( channel, 90)
