import robot
import time

robot = robot.robot()
robot.squat()
robot.downArm()
robot.stand(2000)
time.sleep(5)
robot.oneStep(1000)
time.sleep(3)
robot.toSquat(2000)
#time.sleep(3)

#robot.release()