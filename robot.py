import time
import PCA9685_MG996R

class robot(object):
    m = 90

    T_pose =    [m, m-45, m+45, m+45, m,  m, m+45, m-90,
                m, m+45, m-45, m-45, m,  m, m-45, m+90]
    current_pose = [ robot.T_pose[i] for i in range(16)]

    armDown_pose = [-1,-1,-1,-1,-1, m, m-45, m-90,
                    -1,-1,-1,-1,-1, m, m+45, m+90]
    squat_pose =   [m, m+63, m-74, m-10, m,  -1, -1, -1,
                    m, m-63, m+74, m+10, m,  -1, -1, -1]
    stand_pose =    [m, m+18, m-41, m-27, m,  -1,-1,-1,
                    m, m-18, m+41, m+27, m,  -1,-1,-1]

    _oneStep_pose = (
        ((m+16, m+18, m-41, m-27, m-4,   -1, -1, -1,  m+34, m-11, m+54, m+34, m+8,     -1, -1, -1),750),  # Move center-of-gravity to right-leg, and push left-feet
        ((-1, -1, -1, -1, -1,            -1, -1, -1,  m, m-2, m+67, m+64, -1,    -1, -1, -1),750),   # Raise Left-leg up to the top
        ((-1, -1, -1, m-23, -1,        -1, -1, -1,  m+11, m+18, m+33, m+52, m+4,       -1, -1, -1),750),   # Push Left-foot forward
        ((m, m+29, m-46, m-16, m,      -1, -1, -1,  m, m-4, m+41, m+42, m,         -1, -1, -1),750),   # Stand firm on left-foot
        ((m-19, m+18, m-38, -1, m-6,   -1, -1, -1,  m-13, -1, -1, m+46, m+4,    -1, -1, -1),1500),  # Move center-of-gravity to left-leg
        ((-1, m+2, m-58, m-54, -1,     -1, -1, -1,   -1, -1, -1, m+47, -1,        -1, -1, -1),750),   # Raise Right-leg up and move body forward
        ((m-17, m+6, m-37, m-26, -1,   -1, -1, -1,  -1, m-17, -1, m+25, -1,        -1, -1, -1),750),   # Raise Right-leg down
        ((m, m+18, m-41, m-27, m,      -1, -1, -1,  m, m-18, m+41, m+27, m,     -1, -1, -1),750)   # Stand firm
    )

    oneStep_pose = (
        ((m+16, m+18, m-41, m-27, m-4,   -1, -1, -1,  m+34, m-11, m+54, m+34, m+8,     -1, -1, -1),750),  # Move center-of-gravity to right-leg, and push left-feet
        ((-1, -1, -1, -1, -1,            -1, -1, -1,  m, m-2, m+67, m+64, -1,    -1, -1, -1),750),   # Raise Left-leg up to the top
        ((-1, -1, -1, m-31, -1,        -1, -1, -1,  m+11, m+18, m+33, m+52, m+4,       -1, -1, -1),750),   # Push Left-foot forward
        ((m, m+29, m-46, m-24, m,      -1, -1, -1,  m, m-4, m+41, m+42, m,         -1, -1, -1),750),   # Stand firm on left-foot
        ((m-19, m+18, m-38, -1, m-6,   -1, -1, -1,  m-13, -1, -1, m+46, m+4,    -1, -1, -1),1500),  # Move center-of-gravity to left-leg
        ((-1, m+2, m-58, m-54, -1,     -1, -1, -1,   -1, -1, -1, m+47, -1,        -1, -1, -1),750),   # Raise Right-leg up and move body forward
        ((m-17, m+6, m-37, m-26, -1,   -1, -1, -1,  -1, m-17, -1, m+30, -1,        -1, -1, -1),750),   # Raise Right-leg down
        ((m, m+18, m-41, m-27, m,      -1, -1, -1,  m, m-18, m+41, m+27, m,     -1, -1, -1),750)   # Stand firm
    )

    def __init__(self):
        self.current_pose = [ self.m for i in range(16)]
        self.pwm = PCA9685_MG996R.PCA9685_MG996R()
        frequency = 50
        self.pwm.set_pwm_freq(frequency)

    def downArm(self, ms_time = 500):
        self.current_pose = self.pwm.moveTo( self.current_pose, self.armDown_pose, ms_time)

    def squat(self):
        for i in range(len(self.squat_pose)):
            if 0 <= self.squat_pose[i] :
                self.pwm.rotate_to_angle(i, self.squat_pose[i])
            self.current_pose[i] = self.squat_pose[i]

    def toSquat(self, ms_time = 1000):
        self.current_pose = self.pwm.moveTo( self.current_pose, self.squat_pose, ms_time)
    
    def stand(self, ms_time = 1000):
        self.current_pose = self.pwm.moveTo( self.current_pose, self.stand_pose, ms_time)

    def oneStep(self, ms_time = 750):
        self.current_pose = self.pwm.moveTo( self.current_pose, self.stand_pose, ms_time)
        for i in range(len(self.oneStep_pose)):
            self.current_pose = self.pwm.moveTo( self.current_pose, self.oneStep_pose[i][0], ms_time)

    def release(self):
        self.pwm.set_all_pwm(0,0)
        time.sleep(0.5)
        self.pwm.set_all_pwm(0,0)
