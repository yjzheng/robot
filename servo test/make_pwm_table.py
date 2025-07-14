filename = "dt.dat"
import os
try:
    os.remove(filename)
except:
    pass
import tty, sys, termios
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
set_angle_value = 0
target_angle = 9
pulse = pwm.angle2PWM(channel, target_angle)
pwm.set_pwm(channel, 0, pulse)
time.sleep(1)
target_angle = 90
print("move to angle", target_angle)
#pwm.rotate_to_angle( channel, set_angle_value)
pulse = pwm.angle2PWM(channel, target_angle)
pwm.set_pwm(channel, 0, pulse)
input("Press <Enter> to begin")
target_angle = 0
pulse = pwm.angle2PWM(channel, target_angle)
pwm.set_pwm(channel, 0, pulse)

angle_2_PWM = [0 for i in range(180//5 + 1) ]

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
try:
    current_channel = 0
    while True:
        print("move to target angle:", target_angle)
        keyin =sys.stdin.read(1)[0]
        print("You pressed", keyin)
        if keyin == ']':
            pulse += 1
            pwm.set_pwm(current_channel, 0, pulse)
            print( "channel", current_channel, ":", pulse)
        elif keyin == '[':
            pulse -= 1
            pwm.set_pwm(current_channel, 0, pulse)
            print( "channel", current_channel, ":", pulse)
        elif keyin == '\n':
            angle_2_PWM[target_angle//5] = pulse
            target_angle += 5
            if target_angle > 180:
                # write array to file
                f = open(filename, "w")
                for i in range(len(angle_2_PWM)):
                    f.write(str(angle_2_PWM[i]))
                    if (i % 2) == 0:
                        if( i != len(angle_2_PWM) - 1): 
                            f.write(",")
                    else: 
                        f.write(",\n")
                f.close()

                break
        elif keyin == 'u':
            target_angle -= 5
        if keyin == 'q':
            break
except:
    pass
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

target_angle = 90
print("move to angle", target_angle)
#pwm.rotate_to_angle( channel, set_angle_value)
pulse = pwm.angle2PWM(channel, target_angle)
pwm.set_pwm(channel, 0, pulse)
