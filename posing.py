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

T_pose =    [m, m-45, m+45, m+45, m,  m, m+45, m-90,
            m, m+45, m-45, m-45, m,  m, m-45, m+90]
current_pose = [ T_pose[i] for i in range(16)]


squat_pose =   [m, m+63, m-71, m-8, m,  m-6, m, m-90,
                m, m-63, m+71, m+8, m,  m+6, m, m+90]

stand_pose = [m, m+22, m-50, m-40, m,  m-5, m, m-90,
              m, m-22, m+50, m+40, m,  m+5, m, m+90]

catch_ball = (
    ((m, m+22, m-50, m-40, m,  -1, -1, -1,  m, m-22, m+50, m+40, m,  -1, -1, -1), 500),   # Stand pose
    ((m, m+20, m-70, m-70, m,  -1, -1, m-45,   m, m-20, m+70, m+70, m,  -1,-1,m+45),500),
    ((m, m+25, -1, -1, m,     -1, m-45, -1,   m, m-25, -1, -1, m,    -1, m+45, -1),500),
    ((-1, -1, -1, -1, -1,     -1, m-60, -1,   -1, -1, -1, -1, -1,    -1, m+60, -1),500), # catch
    ((-1, m+20, -1, -1, -1,   -1, -1, m+45,   -1, m-20, -1,-1,-1,    -1, -1, m-45),500),
    ((m, m+22, m-50, m-40, m,  -1, -1, -1,  m, m-22, m+50, m+40, m,  -1, -1, -1), 500),   # Stand pose
    )

oneStep = (
    ((m+15, m+22, m-50, m-40, m-1,   -1, -1, -1,  m+32, m-29, m+54, m+34, m+5,     -1, -1, -1),750),  # Move center-of-gravity to right-leg, and push left-feet
    ((-1, -1, -1, -1, -1,            -1, -1, -1,  m+5, m-24, m+56, m+44, m+10,    -1, -1, -1),750),   # Raise Left-leg up to the top
    ((-1, -1, -1, m-38, -1,        -1, -1, -1,  m+11, m+17, m+34, m+61, -1,       -1, -1, -1),750),   # Push Left-foot forward
    ((m, m+29, m-43, m-21, m,      -1, -1, -1,  m, m+3, m+42, m+54, -1,         -1, -1, -1),750),   # Stand firm on left-foot
    ((m-19, m+18, m-38, -1, m-5,   -1, -1, -1,  m-17, m-21, m+50, m+45, m+1,    -1, -1, -1),750),  # Move center-of-gravity to left-leg
    ((m-7, m+16, m-64, m-55, m-9,     -1, -1, -1,   -1, -1, -1, -1, -1,        -1, -1, -1),750),   # Raise Right-leg up and move body forward
    ((m, m+22, m-50, m-40, m,      -1, -1, -1,  m, m-22, m+50, m+40, m,     -1, -1, -1),750)   # Stand firm
    )

prepare_to_walk = (
    ((m+15, m+21, m-50, m-34, m-1,   -1, -1, -1,  m+32, m-16, m+54, m+34, m+5,     -1, -1, -1),500),  # Move center-of-gravity to right-leg, and push left-feet
    ((-1, -1, -1, -1, -1,            -1, -1, -1,  m+5, m-8, m+56, m+44, m+6,    -1, -1, -1),500),   # Raise Left-leg up to the top
    ((-1, -1, -1, m-34, -1,        -1, -1, -1,  m+11, m+17, m+34, m+61, m+4,       -1, -1, -1),500),   # Push Left-foot forward
    ((m, m+29, m-43, m-21, m,      -1, -1, -1,  m, m+3, m+42, m+49, m,         -1, -1, -1),500)   # Stand firm on left-foot
    )

end_walking = (
    ((m-19, m+18, m-38, -1, m-5,   -1, -1, -1,  m-15, m-21, m+50, m+34, m+1,    -1, -1, -1),500),  # Move center-of-gravity to left-leg
    ((-1, m+2, m-64, m-55, m-9,     -1, -1, -1,   -1, -1, -1, -1, -1,        -1, -1, -1),500),   # Raise Right-leg up and move body forward
    ((m, m+21, m-50, m-34, m,      -1, -1, -1,  m, m-21, m+50, m+34, m,     -1, -1, -1),500)   # Stand firm
    )

right_foot_ahead = (
    ((m, m+39, m-43, m-16, m-2,   -1, -1, -1,    m-15, m-21, m+50, m+34, m+1,         -1, -1, -1),500), 
    ((m-5, m+8, m-56, m-44, m-6,   -1, -1, -1,    -1, -1, -1, -1, -1,         -1, -1, -1),500), 
    ((m-11, m-17, m-34, m-61, m-4,   -1, -1, -1,    -1, -1, -1, m+34, -1,         -1, -1, -1),500), 
    ((m, m+5, m-42, m-49, m,   -1, -1, -1,    m, m-29, m+43, m+21, m,         -1, -1, -1),500), 
    )

left_foot_ahead = (
    ((m+15, m+21, m-50, m-34, m-1,   -1, -1, -1,    m, m-39, m+43, m+16, m+2,         -1, -1, -1),500), 
    ((-1, -1, -1, -1, -1,            -1, -1, -1,  m+5, m-8, m+56, m+44, m+6,    -1, -1, -1),500),   # Raise Left-leg up to the top
    ((-1, -1, -1, m-34, -1,        -1, -1, -1,  m+11, m+17, m+34, m+61, m+4,       -1, -1, -1),500),   # Push Left-foot forward
    ((m, m+29, m-43, m-21, m,      -1, -1, -1,  m, m-5, m+42, m+49, m,         -1, -1, -1),500)   # Stand firm on left-foot
    )

turn_right = (
    ((m-32, m+22, m-54, m-34, m-5,   -1, -1, -1,  m-15, m-21, m+50, m+39, m+1,     -1, -1, -1),750),
    ((m-5, m+16, m-70, m-55, -1,    -1, -1, -1,  -1,-1,-1, m+43, -1,            -1, -1, -1),750),
    ((-1, m+57, m-65, m-21, -1,    -1, -1, -1,  -1,-1,-1, m+50, -1,             -1, -1, -1),750),
    ((m, m+29, m-43, m-21, m,      -1, -1, -1,  m, m-5, m+42, m+49, m,         -1, -1, -1),750),

    ((m, m+23, m-43, m-21, m,      -1, -1, -1,  m, m-11, m+42, m+49, m,         -1, -1, -1),750),
    ((m, m+22, m-50, m-40, m,      -1, -1, -1,  m, m-22, m+50, m+40, m,         -1, -1, -1),750),
)

turn_left = (
    ((m+15, m+21, m-50, m-39, m-1,   -1, -1, -1,  m+32, m-22, m+54, m+34, m+5,     -1, -1, -1),750),
    ((-1,-1,-1, m-43, -1,    -1, -1, -1,  m+5,m-16,m+70, m+55, -1,              -1, -1, -1),750),
    ((-1,-1,-1, m-50, -1,    -1, -1, -1,  -1, m-57, m+65, m+21, -1,             -1, -1, -1),750),
    ((m, m+5, m-42, m-49, m,      -1, -1, -1,  m, m-29, m+43, m+21, m,         -1, -1, -1),750),

    ((m, m+11, m-42, m-49, m,      -1, -1, -1,  m, m-23, m+43, m+21, m,         -1, -1, -1),750),
    ((m, m+22, m-50, m-40, m,      -1, -1, -1,  m, m-22, m+50, m+40, m,         -1, -1, -1),750),
)

pwm.print_adjust()
for i in range(len(squat_pose)):
    if squat_pose[i] != -1:
        #pwm.rotate_to_angle(i, sit_pose[i], adjust)
        pwm.rotate_to_angle(i, squat_pose[i])
        current_pose[i] = squat_pose[i]

time.sleep(1)
current_pose = pwm.moveTo( current_pose, stand_pose, 1000)

time.sleep(1)
for i in range(len(catch_ball)):
    current_pose = pwm.moveTo( current_pose, catch_ball[i][0], catch_ball[i][1])
    #time.sleep(0.5)

#time.sleep(1)
#for i in range(len(oneStep)):
#    current_pose = pwm.moveTo( current_pose, oneStep[i][0], oneStep[i][1])

#time.sleep(1)
#for i in range(len(prepare_to_walk)):
#    current_pose = pwm.moveTo( current_pose, prepare_to_walk[i][0], prepare_to_walk[i][1])

#time.sleep(1)
#for i in range(len(right_foot_ahead)):
#    current_pose = pwm.moveTo( current_pose, right_foot_ahead[i][0], right_foot_ahead[i][1])

#time.sleep(1)
#for i in range(len(left_foot_ahead)):
#    current_pose = pwm.moveTo( current_pose, left_foot_ahead[i][0], left_foot_ahead[i][1])

#time.sleep(1)
#for i in range(len(end_walking)):
#    current_pose = pwm.moveTo( current_pose, end_walking[i][0], end_walking[i][1])

#time.sleep(1)
#for t in range(3):
#for i in range(len(turn_right)):
#    current_pose = pwm.moveTo( current_pose, turn_right[i][0], turn_right[i][1])

#time.sleep(1)
#for i in range(len(turn_left)):
#    current_pose = pwm.moveTo( current_pose, turn_left[i][0], turn_left[i][1])

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