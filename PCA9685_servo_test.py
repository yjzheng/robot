import time
import tty, sys, termios
import PCA9685
# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685.PCA9685(PCA9685.PCA9685_ADDRESS)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# MG996R TEST RESULT : 400 us ~ 2722 us
#define FREQUENCY           50
frequency = 50

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)

for angle in range( 90, 0 - 1, -1):
    for channel in range(16):
        pwm.rotate_to_angle( channel, angle)
    time.sleep(0.05)
for angle in range( 0, 180 + 1, 1):
    for channel in range(16):
        pwm.rotate_to_angle( channel, angle)
    time.sleep(0.05)
for angle in range( 180, 90 - 1, -1):
    for channel in range(16):
        pwm.rotate_to_angle( channel, angle)
    time.sleep(0.05)

channel = 0
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
