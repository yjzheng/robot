import tty, sys, termios
import PCA9685_MG996R

pwm = PCA9685_MG996R.PCA9685_MG996R()

frequency = 50
pwm.set_pwm_freq(frequency)

channel = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
m = 90  # middle
#adjust = [0,2,-3,0,-3, -6,-1,9, -3,-4,6,7,2, 1,-12,-19]
org_pose = [m for i in range(16)]

T_pose =    [m, m-45, m+45, m+45, m,  m, m+45, m-90,
            m, m+45, m-45, m-45, m,  m, m-45, m+90]
current_pose = [ T_pose[i] for i in range(16)]

pwm.print_adjust()
for i in range(len(org_pose)):
    #pwm.rotate_to_angle(i, sit_pose[i], adjust)
    pwm.rotate_to_angle(i, org_pose[i])
##current_pose = pwm.moveTo( sit_pose, stand_pose, 1000, adjust)
current_pose = pwm.moveTo( org_pose, T_pose, 3000)

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
            print('<'+str(current_channel)+','+str(current_pose[current_channel])+','+ str(current_pose[current_channel]-T_pose[current_channel])+'>')

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