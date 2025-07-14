import time
import cv2
import numpy as np
import socket
import zlib
import PCA9685_MG996R

pwm = PCA9685_MG996R.PCA9685_MG996R()
# Initialise the PCA9685 using the default address (0x41).
pwm2 = PCA9685_MG996R.PCA9685_MG996R(PCA9685_MG996R.PCA9685_ADDRESS_2)
frequency = 50
# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(frequency)
pwm2.set_pwm_freq(frequency)

m = 90  # middle

T_pose =    [m, m-45, m+45, m+45, m,  m, m+45, m-90,
            m, m+45, m-45, m-45, m,  m, m-45, m+90]
current_pose = [ T_pose[i] for i in range(16)]

squat_pose =   [m, m+63, m-71, m-20, m,  m-6, m, m-90,
                m, m-63, m+71, m+20, m,  m+6, m, m+90]

stand_pose = [m, m+22, m-50, m-42, m,  m-5, m, m-90,
              m, m-22, m+50, m+42, m,  m+5, m, m+90]

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

oneStep = (
    ((m+15, m+22, m-50, m-40, m-1,   -1, -1, -1,  m+32, m-29, m+54, m+34, m+5,     -1, -1, -1),750),  # Move center-of-gravity to right-leg, and push left-feet
    ((-1, -1, -1, -1, -1,            -1, -1, -1,  m+5, m-24, m+56, m+44, m+10,    -1, -1, -1),750),   # Raise Left-leg up to the top
    ((-1, -1, -1, m-38, -1,        -1, -1, -1,  m+11, m+17, m+34, m+61, -1,       -1, -1, -1),750),   # Push Left-foot forward
    ((m, m+29, m-43, m-21, m,      -1, -1, -1,  m, m+3, m+42, m+54, -1,         -1, -1, -1),750),   # Stand firm on left-foot
    ((m-19, m+18, m-38, -1, m-5,   -1, -1, -1,  m-17, m-21, m+50, m+45, m+1,    -1, -1, -1),750),  # Move center-of-gravity to left-leg
    ((m-7, m+16, m-64, m-55, m-9,     -1, -1, -1,   -1, -1, -1, -1, -1,        -1, -1, -1),750),   # Raise Right-leg up and move body forward
    ((m, m+22, m-50, m-40, m,      -1, -1, -1,  m, m-22, m+50, m+40, m,     -1, -1, -1),750)   # Stand firm
    )

catch_ball = (
    ((m, m+22, m-50, m-40, m,  -1, -1, -1,  m, m-22, m+50, m+40, m,  -1, -1, -1), 500),   # Stand pose
    ((m, m+20, m-70, m-70, m,  -1, -1, m-45,   m, m-20, m+70, m+70, m,  -1,-1,m+45),500),
    ((m, m+25, -1, -1, m,     -1, m-45, -1,   m, m-25, -1, -1, m,    -1, m+45, -1),500),
    ((-1, -1, -1, -1, -1,     -1, m-60, -1,   -1, -1, -1, -1, -1,    -1, m+60, -1),500), # catch
    ((-1, m+20, -1, -1, -1,   -1, -1, m+45,   -1, m-20, -1,-1,-1,    -1, -1, m-45),500),
    ((m, m+22, m-50, m-40, m,  -1, -1, -1,  m, m-22, m+50, m+40, m,  -1, -1, -1), 500),   # Stand pose
    )

for i in range(len(squat_pose)):
    if squat_pose[i] != -1:
        #pwm.rotate_to_angle(i, sit_pose[i], adjust)
        pwm.rotate_to_angle(i, squat_pose[i])
        current_pose[i] = squat_pose[i]

time.sleep(1)
current_pose = pwm.moveTo( current_pose, stand_pose, 1000)

cam_v_servo_angle = 120
pwm2.rotate_to_angle(1, cam_v_servo_angle)

dx = 5
cam_h_servo_angle_dx = -dx
cam_h_min_angle = 45
cam_h_max_angle = 135
array_range = (cam_h_max_angle-cam_h_min_angle) // dx + 1
found_object = [ 0 for i in range(array_range)]
found_object_xy = [(0,0) for i in range(array_range)]

cam_h_servo_angle = 90
pwm2.rotate_to_angle(0, cam_h_servo_angle)

video_index = 0
_frame_width = int(640)
_frame_height = int(480)
while video_index < 2:
    try:
        print("video_index:", video_index)
        cap = cv2.VideoCapture(video_index)
        ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH,_frame_width)
        ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,_frame_height)
        result, frame = cap.read()
        if result: break
    except:
        pass
    video_index += 1

broadcastPort = 55053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # SOCK_DGRAM for UDP
sock.settimeout(None) # Set a timeout on blocking socket operations. blocking mode
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state
#sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#sock.bind((source_ip, source_port))

target_ip = "172.20.10.9"

print("Begin finding")

PS_SCAN     = 1
PS_TURN_TO  = 2
PS_CLOSING  = 3
PS_FINISHED = 4

process_state = PS_SCAN

start_scan = True
found_object_size = 50
ready_to_catch_size = 130

def get_found_object( angle):
    radius = 0
    coordinate = (0,0)
    if cam_h_min_angle < angle < cam_h_max_angle:
        array_index = (angle -cam_h_min_angle) // dx
        radius = found_object[array_index]
        coordinate = found_object_xy[array_index]
    return coordinate, radius

def get_frame_result( video_cap):
    result = ((0,0), 0)
    # Take each frame
    _, frame = video_cap.read()
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # --- select color range ---
    #inRange(hsv, Scalar(175.0, 150.0, 0.0), Scalar(179.0, 255.0, 255.0), mask) // red
    #inRange(hsv, Scalar(0.0, 150.0, 0.0), Scalar(5.0, 255.0, 255.0), mask2)

    # red
    '''
    lower_red = np.array([170,50,50])
    upper_red = np.array([179,255,255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    lower_red = np.array([0,50,50])
    upper_red = np.array([10,255,255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)
    mask = cv2.bitwise_or(mask,mask2)
    '''

    # deep blue
    lower_blue = np.array([105,0,0])
    upper_blue = np.array([130,255,255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
                
    # green
    #lower_green = np.array([60, 0, 0])
    #upper_green = np.array([90, 255, 200])
    #mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # orange / yellow
    '''
    lower_oragne = np.array([5,150,0])
    upper_orange = np.array([20,255,255])
    mask = cv2.inRange(hsv, lower_oragne, upper_orange)
    '''
    
    #blur = cv2.GaussianBlur(mask,(5,5),0)
    #canny_output = cv2.Canny(blur,500,600)
    '''
    lines = cv2.HoughLinesP(canny_output, 2, np.pi/180, 100, np.array([]), minLineLength=50, maxLineGap=30)
    if lines is not None:
        for line in lines:
            x1,y1,x2,y2 = line.reshape(4)
            cv2.line(canny_output,(x1,y1),(x2,y2),(255,0,0),5)
    '''
    # version 3.2
    #img2, contours, hierarchy = cv2.findContours( mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # version 4.
    contours, hierarchy = cv2.findContours( mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0 :
        c = max(contours, key=cv2.contourArea)
        #print('c=',c.shape)
        x,y,w,h = cv2.boundingRect(c)
        #print("w=",w, " h=", h)
        isCircleLike = False
        if w != 0 and h != 0:
            if w > h :
                if (w - h) / w < 0.1:
                    isCircleLike = True
            else:
                if (h - w) / h < 0.1:
                    isCircleLike = True
        if isCircleLike :
            #((x, y), radius) = cv2.minEnclosingCircle(c)
            result = cv2.minEnclosingCircle(c)
            ((x,y), radius) = result
            #print('x,y=',x,y,'radius=', radius )            

            M = cv2.moments(c)
            try:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255,255), 5)
                cv2.circle(frame, center, 5, (0, 255, 255), -1)

            except:
                pass
            '''
            drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
            for i in range(len(contours)):
                #color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
                cv2.drawContours( drawing, contours, i, (0,255,255), 2, cv.LINE_8, hierarchy)
            #cv2.imshow('Contours', drawing)
            '''
            #canny_output = drawing
    else:
        pass
    #cv.imshow('canny',canny_output)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)

    begin_time = time.time()
    data_out = zlib.compress(frame.tobytes())
    end_time = time.time()
    #print("data_out length=", len(data_out)
    #      , " duration:", end_time-begin_time)
    data_out_length = len(data_out)
    header = "fm:" + str(frame.shape[0]) + ':' + str(frame.shape[1]) + ':' + str(frame.shape[2]) + ':' + str(len(data_out))
    sock.sendto(bytes(header, "utf-8"), (target_ip, broadcastPort))
    
    time.sleep(0.001)
    #print("data_out_length=", data_out_length)
    index = 0
    send_length = 1024
    while index < data_out_length:
        if index + send_length > data_out_length:
            send_length = data_out_length - index
            #print("send_length=", send_length)
        sock.sendto(data_out[index:index + send_length], (target_ip, broadcastPort))
        index += send_length

    ##cv2.imshow('mask',mask)
    ##cv2.imshow('res',res)

    return result

try:
    while(1):
        # scan from 90 to min angle, then from 90 to max
        if process_state == PS_SCAN and start_scan == True:

            result = get_frame_result( cap)        
            array_index = (cam_h_servo_angle-cam_h_min_angle)//dx
            found_object[array_index] = int(result[1])
            found_object_xy[array_index] = result[0]
            if found_object_size <= result[1]:
                cam_h_servo_angle = 90
                pwm2.rotate_to_angle(0, cam_h_servo_angle)
                time.sleep(0.5)
                middle_upper_edge = _frame_height // 3 # Height
                middle_lower_edge = _frame_height * 2 // 3
                y = result[0][1]
                if middle_upper_edge < y < middle_lower_edge :
                    pass
                else:
                    if y < middle_upper_edge:
                        cam_v_servo_angle -= dx
                    elif middle_lower_edge < y:
                        cam_v_servo_angle += dx
                    pwm2.rotate_to_angle(1, cam_v_servo_angle)
                    time.sleep(0.5)
                start_scan = False
            else:
                cam_h_servo_angle += cam_h_servo_angle_dx
                if cam_h_servo_angle < cam_h_min_angle:
                    cam_h_servo_angle_dx = -cam_h_servo_angle_dx
                    cam_h_servo_angle = 90
                if cam_h_max_angle < cam_h_servo_angle:
                    cam_h_servo_angle_dx = -cam_h_servo_angle_dx
                    cam_h_servo_angle = 90
                    start_scan = False
                pwm2.rotate_to_angle(0, cam_h_servo_angle)
                time.sleep(0.5)

        if process_state == PS_SCAN and start_scan == False:
            middle_left_edge = frame.shape[0] // 3   # width
            middle_right_edge = frame.shape[0] * 2 // 3  
            middle_xy, middle_radius = get_found_object( 90)
            print(middle_xy,middle_radius)
            print("found_object_size=",found_object_size)
            print("middle_left_edge=",middle_left_edge)
            print("middle_right_edge=",middle_right_edge)
            if found_object_size <= middle_radius and middle_left_edge <= middle_xy[0] <= middle_right_edge:
                #process_state = PS_CLOSING
                print("state: closing")
                if ready_to_catch_size <= middle_radius:
                    print("Catching!")
                    for i in range(len(catch_ball)):
                        current_pose = pwm.moveTo( current_pose, catch_ball[i][0], catch_ball[i][1]) 
                    time.sleep(1)
                    process_state = PS_FINISHED
                    cap.release()
                    while True: pass
                    break

                for i in range(len(oneStep)):
                    current_pose = pwm.moveTo( current_pose, oneStep[i][0], oneStep[i][1]) 
                time.sleep(1)

                if cam_v_servo_angle < 150:
                    cam_v_servo_angle += dx
                    pwm2.rotate_to_angle(1, cam_v_servo_angle)
                    print("v:", cam_v_servo_angle)
                    time.sleep(0.5)

            else:
                turn_to = 0 # left:<1, middle/not found: 0, right:>1

                for i in range(len(found_object)):
                    print("Angle:", i * dx + cam_h_min_angle, " found:", found_object[i])
                    if found_object_size < found_object[i] and i != len(found_object)//2:
                        if i < len(found_object)//2:
                            turn_to += 1
                        else:
                            turn_to -= 1
                print("turn_to=", turn_to)
                # make turn
                if turn_to == 0:
                    '''
                    middle_xy, middle_radius = get_found_object( 90)
                    print("90 degree:", middle_xy, middle_radius)
                    if found_object_size <= middle_radius:
                        if middle_xy[0] < frame.shape[0]//2:
                            turn_to = -1
                        else:
                            turn_to = 1
                    '''
                    middle_xy, middle_radius = get_found_object( 90)
                    print("90 degree:", middle_xy, middle_radius)
                    '''
                    if ready_to_catch_size <= middle_radius:
                        print("Catching!")
                        for i in range(len(catch_ball)):
                            current_pose = pwm.moveTo( current_pose, catch_ball[i][0], catch_ball[i][1]) 
                        time.sleep(3)
                        process_state = PS_FINISHED
                        while True: pass
                        break
                    '''
                    if found_object_size <= middle_radius:
                        if middle_radius < ready_to_catch_size:
                            for i in range(len(oneStep)):
                                current_pose = pwm.moveTo( current_pose, oneStep[i][0], oneStep[i][1]) 
                            time.sleep(1)
                        if cam_v_servo_angle < 150:
                            cam_v_servo_angle += dx
                            pwm2.rotate_to_angle(1, cam_v_servo_angle)
                            print("v:", cam_v_servo_angle)
                        else:
                            print("cam_v_serv_angle too close to the edge:", cam_v_servo_angle)            
                if 0 < turn_to:
                    for i in range(len(turn_right)):
                        current_pose = pwm.moveTo( current_pose, turn_right[i][0], turn_right[i][1]) 
                elif turn_to < 0:
                    for i in range(len(turn_left)):
                        current_pose = pwm.moveTo( current_pose, turn_left[i][0], turn_left[i][1]) 
                time.sleep(1)
            cam_h_servo_angle_dx = -dx
            cam_h_servo_angle = 90
            found_object = [ 0 for i in range(array_range)]
            start_scan = True

except KeyboardInterrupt:
    print('KeyboardInterrupt')

cap.release()

#pwm.print_adjust()
for i in range(len(squat_pose)):
    pwm.rotate_to_angle(i, squat_pose[i])
    current_pose[i] = squat_pose[i]

time.sleep(1)
for i in range(16):
    pwm.set_pwm(i, 0, 0)
time.sleep(0.5)
pwm.set_all_pwm(0,0)
time.sleep(0.5)
pwm.set_all_pwm(0,0)
time.sleep(0.5)