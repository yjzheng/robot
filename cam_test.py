import tty, sys, termios
import time
import PCA9685_MG996R

# Initialise the PCA9685 using the default address (0x41).
pwm = PCA9685_MG996R.PCA9685_MG996R(PCA9685_MG996R.PCA9685_ADDRESS_2)


# MG996R TEST RESULT : 400 us ~ 2722 us
#define FREQUENCY           50
frequency = 50
# 500 us = 0 degree
# 1500 us = 90 degree
# 2500 us = 180 degree

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)
channel = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
m = 90  # middle
#adjust = [0,2,-3,0,-3, -6,-1,9, -3,-4,6,7,2, 1,-12,-19]
current_pose = [ 90 for i in range(16)]
stand_pose = [m, m+18, m-41, m-22, m,  m-5, m, m-90,
              m, m-18, m+41, m+22, m,  m+5, m, m+90]
pwm.print_adjust()
pwm.rotate_to_angle(0, 90)

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
try:
    current_channel = 0
    while True:
        keyin =sys.stdin.read(1)[0]
        print("You pressed", keyin)
        in_channel = channel.get(keyin,-1)
        if in_channel != -1:
            current_channel = in_channel
            print('<'+str(current_channel)+','+str(current_pose[current_channel])+','+ str(current_pose[current_channel]-90)+'>')
        if keyin == ']':
            #current_pwm[current_channel] += 10
            #pwm.set_pwm(current_channel,0,current_pwm[current_channel])
            #print(current_channel,current_pwm[current_channel])
            current_pose[current_channel] += 1
            #pwm.rotate_to_angle( current_channel, current_pose[current_channel], adjust)
            pwm.rotate_to_angle( current_channel, current_pose[current_channel])
            print( current_channel, current_pose[current_channel])
        if keyin == '[':
            #current_pwm[current_channel] -= 10
            #pwm.set_pwm(current_channel,0,current_pwm[current_channel])
            #print(current_channel,current_pwm[current_channel])
            current_pose[current_channel] -= 1
            #pwm.rotate_to_angle( current_channel, current_pose[current_channel], adjust)
            pwm.rotate_to_angle( current_channel, current_pose[current_channel])
            print( current_channel, current_pose[current_channel])
        if keyin == 'q':
            break
except:
    pass
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)