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
#adjust = [0,2,-3,0,-3, -6,-1,9, -3,-4,6,7,2, 1,-12,-19]
current_pose = [ 0 for i in range(16)]
sit_pose =   [m, m+56, m-61, m-5, m,  m-6, m, m-90,
              m, m-56, m+61, m+5, m,  m+6, m, m+90]
#stand_pose = [m, m+19, m-30, m-19, m-2,  m-5, m-70, m-90,  
#              m, m-19, m+30, m+19, m+2,  m+5, m+70, m+90]
#stand_pose = [m, m-3, m-7, m-14, m-4,  m-5, m, m-90,
#              m, m+3, m+7, m+14, m+4,  m+5, m, m+90]

pose1_1= [m+12, m-3, m-9, m-11, m-3,  m-5, m, m-90,
            m+10, m+3, m+7, m+11, m+4,  m+5, m, m+90]
pose1_2 = [m+12, m-3, m-9, m-7, m-3,  m-5, m, m-90,
            m, m+18, m+6, m+23, m+10,  m+5, m, m+90]
pose1_3 = [m, m+5, m-2, m+4, m-4,  m-5, m, m-90,
            m, m+18, m+6, m+23, m+4,  m+5, m, m+90]

pose2_1 = [m-10, m+15, m-23, m+4, m-10,  m-5, m, m-90,
            m-12, m+3, m+9, m+11, m+3,  m+5, m, m+90]
pose2_2 = [m, m-18, m-6, m-23, m-10,  m-5, m, m-90,
            m-12, m+3, m+9, m+11, m+3,  m+5, m, m+90]
pose2_3 = [m, m-18, m-6, m-23, m-4,   m-5, m, m-90,
            m, m-5, m+2, m-4, m+4,  m+5, m, m+90]

stand_pose = [m, m+16, m-41, m-29, m,  m-5, m, m-90,
              m, m-16, m+41, m+29, m,  m+5, m, m+90]
oneStep = (
    ((m+14, m+16, m-46, m-37, m-4,   -1, -1, -1,  m+32, m-16, m+54, m+34, m+1,     -1, -1, -1),750),  # Move center-of-gravity to right-leg, and push left-feet
    ((-1, -1, -1, -1, -1,            -1, -1, -1,  m, m-9, m+67, m+64, m+7,    -1, -1, -1),750),   # Raise Left-leg up to the top
    ((-1, -1, -1, m-34, -1,        -1, -1, -1,  m+11, m+22, m+34, m+59, m+4,       -1, -1, -1),750),   # Push Left-foot forward
    ((m, m+29, m-43, m-19, m,      -1, -1, -1,  m, m+3, m+42, m+48, m+4,         -1, -1, -1),750),   # Stand firm on left-foot
    ((m-19, m+18, m-38, -1, m-7,   -1, -1, -1,  m-13, m-4, m+36, m+44, m+4,    -1, -1, -1),1500),  # Move center-of-gravity to left-leg
    ((-1, m+2, m-56, m-55, m-9,     -1, -1, -1,   -1, m-16, m+46, m+32, -1,        -1, -1, -1),750),   # Raise Right-leg up and move body forward
    ((m-17, m+24, m-37, m-26, -1,   -1, -1, -1,  -1, -1, -1, m+37, -1,        -1, -1, -1),750),   # Raise Right-leg down
    ((m, m+16, m-41, m-29, m,      -1, -1, -1,  m, m-16, m+41, m+29, m,     -1, -1, -1),750)   # Stand firm
    )

pwm.print_adjust()
for i in range(len(sit_pose)):
    #pwm.rotate_to_angle(i, sit_pose[i], adjust)
    pwm.rotate_to_angle(i, sit_pose[i])
    current_pose[i] = sit_pose[i]

time.sleep(1)
##current_pose = pwm.moveTo( sit_pose, stand_pose, 1000, adjust)
current_pose = pwm.moveTo( sit_pose, stand_pose, 1000)

time.sleep(1)
for i in range(len(oneStep)):
    current_pose = pwm.moveTo( current_pose, oneStep[i][0], oneStep[i][1])
    #time.sleep(0.5)

#time.sleep(1)
#current_pose = pwm.moveTo( current_pose, oneStep_2, 750)
#time.sleep(1)
#current_pose = pwm.moveTo( current_pose, oneStep_3, 750)
#time.sleep(1)
#current_pose = pwm.moveTo( current_pose, oneStep_4, 1000)
#time.sleep(1)
#current_pose = pwm.moveTo( current_pose, oneStep_5, 750)
#time.sleep(1)
#current_pose = pwm.moveTo( current_pose, oneStep_6, 750)
#current_pose = pwm.moveTo( current_pose, stand_pose, 500)
#time.sleep(3)
#current_pose = pwm.moveTo( current_pose, sit_pose, 1000)

'''
for i in range(3):
    current_pose = pwm.moveTo( current_pose, holdByRightLeg_1, 1000)
    current_pose = pwm.moveTo( current_pose, holdByRightLeg_2, 1000)
    current_pose = pwm.moveTo( current_pose, holdByRightLeg_3, 1000)
    current_pose = pwm.moveTo( current_pose, holdByRightLeg_4, 1000)
    current_pose = pwm.moveTo( current_pose, LeftPush_1, 1000)
    current_pose = pwm.moveTo( current_pose, LeftPush_2, 1000)
    current_pose = pwm.moveTo( current_pose, holdByLeftLeg_1, 1000)
    current_pose = pwm.moveTo( current_pose, holdByLeftLeg_2, 1000)
    current_pose = pwm.moveTo( current_pose, holdByLeftLeg_3, 1000)
    current_pose = pwm.moveTo( current_pose, holdByLeftLeg_4, 1000)
    current_pose = pwm.moveTo( current_pose, RightPush_1, 1000)
    current_pose = pwm.moveTo( current_pose, RightPush_2, 1000)
'''

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