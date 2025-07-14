import time
import cv2
import numpy as np
import socket
import lzma
import zlib

_frame_width = int(640)
_frame_height = int(480)
cap = cv2.VideoCapture(0)
ret = cap.set(cv2.CAP_PROP_FRAME_WIDTH,_frame_width)
ret = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,_frame_height)

broadcastPort = 55053

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # SOCK_DGRAM for UDP
sock.settimeout(None) # Set a timeout on blocking socket operations. blocking mode
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state
#sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#sock.bind((source_ip, source_port))

target_ip = "172.20.10.9"

print("Beginning")
try:
   begin_time = time.time()
   while True:
        if (time.time() - begin_time) > 1.0:
            begin_time = time.time()
            _, frame = cap.read()
            end_time = time.time()
            #print("capture read duration:", end_time - begin_time)
            '''
            #transfer_data = frame.reshape(-1)
            send_data = frame.reshape((_frame_height,_frame_width * 3))
            #print("send_data:", send_data.shape)
            header = "fm:" + str(frame.shape[0]) + ':' + str(frame.shape[1]) + ':' + str(frame.shape[2])
            sock.sendto(bytes(header, "utf-8"), (target_ip, broadcastPort))
            count = 0
            for data in send_data:
                sock.sendto(bytes(data), (target_ip, broadcastPort))
                count += 1
            '''
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

        else:
            time.sleep(0.001)
except KeyboardInterrupt:
    print('KeyboardInterrupt')
except Exception as e: 
    print(e)
    pass

cap.release()
