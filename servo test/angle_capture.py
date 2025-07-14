import time
import tty, sys, termios
import cv2
import PCA9685_MG996R
# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685_MG996R.PCA9685_MG996R(PCA9685_MG996R.PCA9685_ADDRESS)

_frame_width = int(800)
_frame_height = int(600)
cap = cv2.VideoCapture(0)
#ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH,_frame_width)
#ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,_frame_height)

#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('output.avi', fourcc, 20.0, (_frame_width,  _frame_height))

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# MG996R TEST RESULT : 400 us ~ 2722 us
#define FREQUENCY           50
frequency = 50

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)

channel = 0
print("move to angle 90")
pwm.rotate_to_angle( channel, 90)
input("Press Enter to continue.")
for angle in range(0, 180+1, 5):
    print("angle:",angle)
    pwm.rotate_to_angle( channel, angle)
    time.sleep(1.5)
    _, image = cap.read()
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, str(angle), (200,100), font, 4, (255,255,255), 5, cv2.LINE_AA)
    file_name = "Capture%3s.jpg" % str(angle)
    file_name = file_name.replace(' ','0')
    cv2.imwrite(file_name, image)
    #take a picture and mark angle, and write to file with name
    #time.sleep(1)

cap.release()

pwm.rotate_to_angle( channel, 90)

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
pulse_width = 1500
while True:
    keyin =sys.stdin.read(1)[0]
    if keyin == ']':
        pulse_width += 1
        pwm.set_servo_pulse(channel, pulse_width)
        print( pulse_width)
    if keyin == '[':
        pulse_width -= 1
        pwm.set_servo_pulse(channel, pulse_width)
        print( pulse_width)
    if keyin == 'q':
        break
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
