#import logging
import time
import math
import smbus

# Registers/etc:
PCA9685_ADDRESS    = 0x40
PCA9685_ADDRESS_2  = 0x41
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

def angle_to_pulsewidth( angle):
    #pulse_length = 1000000    # 1,000,000 us per second
    #pulse_length //= frequency       # 50 Hz = 20ms = 20000us
    #pulse_length //= 4096     # 12 bits of resolution (=4.88us)
    
    pulse_width = int((2000 * angle / 180 + 500) / 4.8828125)
    #pulse_width = int((2000 * angle / 180 + 500) / 4.65)
    return pulse_width

class PCA9685_MG996R(object):
    """PCA9685 PWM LED/servo controller."""
    servoDeviationTable = [[0 for i in range(36+1)] for j in range(16)] #180/5 + 1, count by every 5 degree
    adjustArray = [ 0 for i in range(16)]
    #angle2PWM_Table = [ angle_to_pulsewidth(angle) for angle in range(180+1) ]  
    angle2PWM_Table = [[ angle_to_pulsewidth(angle) for angle in range(180+1) ] for i in range(16)]

    def __init__(self, address=PCA9685_ADDRESS):
        """Initialize the PCA9685."""
        if address == PCA9685_ADDRESS:
            try:
                #print("try to open deviation tables")
                for number in range(16):
                    filename = "deviation" + str(number) + ".table"
                    f = open(filename, "r")
                    data = f.read()
                    f.close()
                    #print(data)
                    array = data.split(',')
                    print("length=", len(array))
                    if len(array) == 36+1:  #180/5 + 1, count by every 5 degree
                        for i in range(36+1):
                            self.servoDeviationTable[number][i] =int(array[i])
                        print(number,':',self.servoDeviationTable[number])
            except: #IOError
                pass
            try:
                #print("try to open deviation tables")
                for number in range(16):
                    filename = "dt%2s.dat" % str(number)
                    filename = filename.replace(' ','0')
                    #print("filename: "+filename)
                    f = open(filename, "r")
                    data = f.read()
                    f.close()
                    #print(data)
                    array = data.split(',')
                    #print("length=", len(array))
                    if len(array) == 36+1:  #180/5 + 1, count by every 5 degree
                        for item in range(36+1):
                            #print("item=",item)
                            value = int(array[item])
                            #print("value:",value)
                            if item < 36 :
                                next_value = int( array[item+1])
                                diff = next_value - value
                                for index in range(5):
                                    self.angle2PWM_Table[number][item*5+index] = value + int(index * diff / 5 + 0.5)
                            else:
                                self.angle2PWM_Table[number][item*5] = value
                        print(number,':',self.angle2PWM_Table[number])
            except:
                pass
            try:
                #print("try to open adjust.dat")
                f = open("adjust.dat", "r")
                data = f.read()
                f.close()
                #print(data)
                array = data.split(',')
                if len(array) == 16:
                    for i in range(16):
                        self.adjustArray[i] = int(array[i])
                    print("adjustArray=", self.adjustArray)
            except: #IOError
                pass
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

    def print_adjust(self):
        print(self.adjustArray)

    def set_pwm_freq(self, freq_hz):
        """Set the PWM frequency to the provided value in hertz."""
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        #logger.debug('Setting PWM frequency to {0} Hz'.format(freq_hz))
        #logger.debug('Estimated pre-scale: {0}'.format(prescaleval))
        prescale = int(math.floor(prescaleval + 0.5))
        #logger.debug('Final pre-scale: {0}'.format(prescale))
        #print("prescale=",prescale)
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
        print("channel:"+str(channel)+",on:"+str(on)+",off:"+str(off))
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

    # Idealy:
    #   500 us = 0 degree
    #   1500 us = 90 degree
    #   2500 us = 180 degree

    # 50Hz = 20ms
    # PCA9685 outputs = 12-bit = 4096 steps
    # The minimute pulse = 4.88us

    # Helper function to make setting a servo pulse width simpler.
    # pulse : 0.5(ms) -> 0 degree, 1.5(ms) -> 90 degree, 2.5(ms) -> 180 
    def set_servo_pulse(self, channel, pulse):
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
        pulse //= 4.8828125 # input: pulse range 600 ~ 2600 us or 500 ~ 2500 us
        self.set_pwm(channel, 0, int(pulse))

    def angle2PWM(self, channel, angle, adjustArray = adjustArray):
        print("channel=",channel, "angle=",angle)
        angle += adjustArray[channel]
        print("after adjusted angle=", angle)
        if 180 < angle : angle = 180
        elif angle < 0 : angle = 0
        finalAngle = angle + self.servoDeviationTable[channel][angle//5]
        print("final angle:", finalAngle)
        if finalAngle < 0:
            finalAngle = 0
        elif 180 < finalAngle:
            finalAngle = 180
        return self.angle2PWM_Table[channel][finalAngle]

    def rotate_to_angle(self, channel, angle, adjustArray = adjustArray):
        pulse = self.angle2PWM(channel, angle, adjustArray)
        self.set_pwm(channel, 0, pulse)

    def moveTo(self, currentAngleList, targetAngleList, duration, adjustArray = adjustArray): # duration unit is ms
        #print(adjustArray)
        now_ms = int(time.time()*1000)
        StepTimeoutList = []
        directionLIst = []
        TimeoutList = []
        # convert angle to pulse value in the chip
        currentPulseWidthList = []
        targetPulseWidthList = []
        _targetAngleList = [ targetAngleList[i] for i in range(len(targetAngleList))]
        for i in range(len(adjustArray)):
            #print(currentAngleList[i],' -> ',_targetAngleList[i])
            StepTimeoutList.append(0)
            directionLIst.append(0)
            TimeoutList.append(0.0)
            currentPulseWidth = 0
            targetPulseWidth = 0
            if currentAngleList[i] < 0 and 0 <= _targetAngleList[i]:
                #targetPulseWidth = angle_to_pulsewidth( _targetAngleList[i]+adjustArray[i])
                targetPulseWidth = self.angle2PWM(i, _targetAngleList[i], adjustArray)
                self.set_pwm(i, 0, targetPulseWidth)
            elif currentAngleList[i] == _targetAngleList[i] or _targetAngleList[i] < 0:
                _targetAngleList[i] = currentAngleList[i]
                directionLIst[i] = 0
                TimeoutList[i] = 0
            else:
                #currentPulseWidth = angle_to_pulsewidth( currentAngleList[i]+adjustArray[i])
                currentPulseWidth = self.angle2PWM(i, currentAngleList[i], adjustArray)
                #targetPulseWidth = angle_to_pulsewidth( _targetAngleList[i]+adjustArray[i])
                targetPulseWidth = self.angle2PWM(i, _targetAngleList[i], adjustArray)
                if currentPulseWidth > targetPulseWidth:
                    StepTimeoutList[i] = duration / (currentPulseWidth - targetPulseWidth)
                    directionLIst[i] = -1
                    TimeoutList[i] = now_ms + StepTimeoutList[i]
                else:
                    StepTimeoutList[i] = duration / (targetPulseWidth - currentPulseWidth)
                    directionLIst[i] = 1
                    TimeoutList[i] = now_ms + StepTimeoutList[i]

            currentPulseWidthList.append(currentPulseWidth)
            targetPulseWidthList.append(targetPulseWidth)

        #print(">>now:"+str(int(time.time()*1000)))
        while True:
            now_ms = int(time.time()*1000)
            #print('now(ms):'+str(now_ms))
            needContinue = False
            for i in range(len(TimeoutList)):
                if directionLIst[i] != 0 and now_ms >= TimeoutList[i]:
                    #print('now(ms):'+str(now_ms))
                    TimeoutList[i] = now_ms + StepTimeoutList[i]
                    currentPulseWidthList[i] += directionLIst[i]
                    self.set_pwm(i, 0, currentPulseWidthList[i])
                    #print('current pulsewith:' + str(currentPulseWidthList[i]) + ',target :' + str(targetPulseWidthList[i]))
                    if currentPulseWidthList[i] == targetPulseWidthList[i]:
                        directionLIst[i] = 0
                if directionLIst[i] != 0:
                    needContinue = True
            if needContinue == False:
                #print('break!')
                break
            time.sleep(0.0005)
        #print("<<now:"+str(now_ms))
        return _targetAngleList
