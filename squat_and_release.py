import tty, sys, termios
import time
#import PCA9685
import PCA9685_MG996R

# Initialise the PCA9685 using the default address (0x40).
#pwm = PCA9685.PCA9685()
pwm = PCA9685_MG996R.PCA9685_MG996R()

# MG996R TEST RESULT : 400 us ~ 2722 us
#define FREQUENCY           50
frequency = 50
# 600 us = 0 degree
# 1600 us = 90 degree
# 2600 us = 180 degree

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)
channel = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
m = 90  # middle

current_pose = [ 0 for i in range(16)]

squat_pose =   [m, m+63, m-71, m-8, m,  m-6, m, m-90,
                m, m-63, m+71, m+8, m,  m+6, m, m+90]


pwm.print_adjust()
for i in range(len(squat_pose)):
    pwm.rotate_to_angle(i, squat_pose[i])
    current_pose[i] = squat_pose[i]

time.sleep(1)
pwm.set_pwm_freq(frequency)
pwm.set_all_pwm(0,0)
time.sleep(0.5)
pwm.set_all_pwm(0,0)
time.sleep(0.5)
