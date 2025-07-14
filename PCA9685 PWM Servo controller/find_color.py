import tty, sys, termios
import select
import os
import time
import cv2
import numpy as np
import socket
import PCA9685_MG996R

# Initialise the PCA9685 using the default address (0x41).
pwm2 = PCA9685_MG996R.PCA9685_MG996R(PCA9685_MG996R.PCA9685_ADDRESS_2)
frequency = 50
# Set frequency to 50hz, good for servos.
pwm2.set_pwm_freq(frequency)

cam_h_servo_angle_dx = 5
cam_h_min_angle = 45
cam_h_max_angle = 135
cam_v_servo_angle = 120
pwm2.rotate_to_angle(1, cam_v_servo_angle)

cam_h_servo_angle = 90
pwm2.rotate_to_angle(0, cam_h_servo_angle)
start_scan = True

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

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
ubuf_stdin = os.fdopen(sys.stdin.fileno(), 'rb', buffering=0)

h_lower = 105
h_upper = 130

try:
    begin_time = time.time()
    while(1):
        # Take each frame
        _, frame = cap.read()
        if select.select([ubuf_stdin], [], [], 0)[0] == [ubuf_stdin]:
            keyin = ubuf_stdin.read(1).decode()
            print("keyin:", keyin)
            if keyin == 'q': break
            if keyin == '[':
                cam_h_servo_angle += cam_h_servo_angle_dx
                pwm2.rotate_to_angle(0, cam_h_servo_angle)
                print("cam_h_servo_angle=", cam_h_servo_angle)
            if keyin == ']':
                cam_h_servo_angle -= cam_h_servo_angle_dx
                pwm2.rotate_to_angle(0, cam_h_servo_angle)
                print("cam_h_servo_angle=", cam_h_servo_angle)
            if keyin == 'p':
                cam_v_servo_angle -= 1
                pwm2.rotate_to_angle(1, cam_v_servo_angle)
                print("cam_v_servo_angle=", cam_v_servo_angle)
            if keyin == ';':
                cam_v_servo_angle += 1
                pwm2.rotate_to_angle(1, cam_v_servo_angle)
                print("cam_v_servo_angle=", cam_v_servo_angle)
            if keyin == 'e':
                h_lower -= 1
                print("h_lower=", h_lower)
            if keyin == 'r':
                h_lower += 1
                print("h_lower=", h_lower)
            if keyin == 'd':
                h_upper -= 1
                print("h_upper=", h_upper)
            if keyin == 'f':
                h_upper += 1
                print("h_upper=", h_upper)

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

        ## blue
        #lower_blue = np.array([105,0,0])
        #upper_blue = np.array([130,255,255])
        #mask = cv2.inRange(hsv, lower_blue, upper_blue)
                    
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
        
        lower = np.array([h_lower, 0, 0])
        upper = np.array([h_upper, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

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
            #test
            isCircleLike = True
            if isCircleLike :
                inMiddle = False
                isCircleLike = False
                middle_left_edge = mask.shape[0] * 2 // 5   # width
                middle_right_edge = mask.shape[0] * 3 // 5  
                if middle_left_edge <= x <= middle_right_edge:
                    inMiddle = True

                ((x, y), radius) = cv2.minEnclosingCircle(c)
                print('x,y=',x,y,'radius=', radius )
                #found_object[(cam_h_servo_angle-cam_h_min_angle)//cam_h_servo_angle_dx] = int(radius)

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

        if (time.time() - begin_time) > 1.0:
            begin_time = time.time()
            #transfer_data = frame.reshape(-1)
            send_data = frame.reshape((_frame_height,_frame_width * 3))
            #print("send_data:", send_data.shape)
            header = "fm:" + str(frame.shape[0]) + ':' + str(frame.shape[1]) + ':' + str(frame.shape[2])
            sock.sendto(bytes(header, "utf-8"), (target_ip, broadcastPort))
            count = 0
            for data in send_data:
                time.sleep(0.001)
                sock.sendto(bytes(data), (target_ip, broadcastPort))
                count += 1
        else:
            time.sleep(0.001)

        ##cv2.imshow('mask',mask)
        ##cv2.imshow('res',res)


except KeyboardInterrupt:
    print('KeyboardInterrupt')
except Exception as e:
    print(e)
    pass

cap.release()

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)

ubuf_stdin.close()
