import logging
import time
import math
import smbus
import tty, sys, termios

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)

# Registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04


logger = logging.getLogger(__name__)


def software_reset(i2c=None, **kwargs):
    """Sends a software reset (SWRST) command to all servo drivers on the bus."""
    # Setup I2C interface for device 0x00 to talk to all of them.
    import smbus
    if i2c is None:
        import Adafruit_GPIO.I2C as I2C
        i2c = I2C
    self._device = i2c.get_i2c_device(0x00, **kwargs)
    self._device.writeRaw8(0x06)  # SWRST


class PCA9685(object):
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, address=PCA9685_ADDRESS):
        """Initialize the PCA9685."""
        # Setup I2C interface for the device.
        self._bus = smbus.SMBus(1)
        self._address = address
        self.set_all_pwm(0, 0)
        self._bus.write_i2c_block_data(self._address, MODE2, [OUTDRV])
        self._bus.write_i2c_block_data(self._address, MODE1, [ALLCALL])
        time.sleep(0.005)  # wait for oscillator
        mode1 = self._bus.read_i2c_block_data(self._address, MODE1)
        mode1 = mode1[0] & ~SLEEP  # wake up (reset sleep)
        self._bus.write_i2c_block_data(self._address, MODE1, [mode1])
        time.sleep(0.005)  # wait for oscillator

    def set_pwm_freq(self, freq_hz):
        """Set the PWM frequency to the provided value in hertz."""
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        logger.debug('Setting PWM frequency to {0} Hz'.format(freq_hz))
        logger.debug('Estimated pre-scale: {0}'.format(prescaleval))
        prescale = int(math.floor(prescaleval + 0.5))
        logger.debug('Final pre-scale: {0}'.format(prescale))
        oldmode = self._bus.read_i2c_block_data(self._address, MODE1)
        oldmode = oldmode[0]
        newmode = (oldmode & 0x7F) | 0x10    # sleep
        self._bus.write_i2c_block_data(self._address, MODE1, [newmode])  # go to sleep
        self._bus.write_i2c_block_data(self._address, PRESCALE, [prescale])
        self._bus.write_i2c_block_data(self._address, MODE1, [oldmode])
        time.sleep(0.005)
        self._bus.write_i2c_block_data(self._address, MODE1, [oldmode | 0x80])

    def set_pwm(self, channel, on, off):
        """Sets a single PWM channel."""
        self._bus.write_i2c_block_data(self._address, LED0_ON_L+4*channel, [on & 0xFF])
        self._bus.write_i2c_block_data(self._address, LED0_ON_H+4*channel, [on >> 8])
        self._bus.write_i2c_block_data(self._address, LED0_OFF_L+4*channel, [off & 0xFF])
        self._bus.write_i2c_block_data(self._address, LED0_OFF_H+4*channel, [off >> 8])

    def set_all_pwm(self, on, off):
        """Sets all PWM channels."""
        self._bus.write_i2c_block_data(self._address, ALL_LED_ON_L, [on & 0xFF])
        self._bus.write_i2c_block_data(self._address, ALL_LED_ON_H, [on >> 8])
        self._bus.write_i2c_block_data(self._address, ALL_LED_OFF_L, [off & 0xFF])
        self._bus.write_i2c_block_data(self._address, ALL_LED_OFF_H, [off >> 8])


# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
#define MIN_PULSE_WIDTH       544
#define MAX_PULSE_WIDTH       2400
#define FREQUENCY           50
frequency = 50
# 75~535, average = 535-75 / 2 + 75 = 305(90degree)

# 50Hz = 20ms
# PCA9685 outputs = 12-bit = 4096 steps
# The minimute pulse = 4.88us
# 2.5% of 20ms = 0.5ms ; 12.5% of 20ms = 2.5ms
# 2.5% of 4096 = 102 steps; 12.5% of 4096 = 512 steps

# Helper function to make setting a servo pulse width simpler.
# pulse : 0.5(ms) > 0 degree, 1.5(ms) > 90 degree, 2.5(ms) > 180 
def set_servo_pulse(channel, pulse):
    '''
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= frequency       # 50 Hz = 20ms = 20000us
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution (=4.88us)
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000               # ms to us
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)
    '''
    pulse //= 4.8828125 # input: pulse range 500 ~ 2500 us
    pwm.set_pwm(channel, 0, int(pulse))

def rotate_to_angle(channel, angle):
    if 0 <= angle <= 180:
        pulse_width = 2000 * angle / 180 + 500
        set_servo_pulse(channel, pulse_width)

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)
channel = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
#current_pwm = [375 for i in range(16)]
#current_pwm = [335, 450, 125, 160, 335,  285, 145, 115,  335, 185, 510, 470, 335,  355, 505, 505]

#for i in range(len(current_pwm)):
#    pwm.set_pwm(i, 0, current_pwm[i])

current_angle = [102, 152, 9, 25, 102, 80, 18, 5, 102, 36, 179, 161, 102, 111, 176, 176]
current_channel = 0
while True:
    keyin =sys.stdin.read(1)[0]
    print("You pressed", keyin)
    in_channel = channel.get(keyin,-1)
    if in_channel != -1:
        current_channel = in_channel
    if keyin == ']':
        #current_pwm[current_channel] += 10
        #pwm.set_pwm(current_channel,0,current_pwm[current_channel])
        #print(current_channel,current_pwm[current_channel])
        current_angle[current_channel] += 1
        rotate_to_angle( current_channel, current_angle[current_channel])
        print( current_channel, current_angle[current_channel])
    if keyin == '[':
        #current_pwm[current_channel] -= 10
        #pwm.set_pwm(current_channel,0,current_pwm[current_channel])
        #print(current_channel,current_pwm[current_channel])
        current_angle[current_channel] -= 1
        rotate_to_angle( current_channel, current_angle[current_channel])
        print( current_channel, current_angle[current_channel])
    if keyin == 'q':
        break
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)