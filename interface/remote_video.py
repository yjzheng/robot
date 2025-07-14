import time
import socket
import cv2
import numpy as np
import zlib

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)    # SOCK_DGRAM for UDP
sock.settimeout(None) # Set a timeout on blocking socket operations.
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state

broadcastPort = 55053

source_ip="0.0.0.0"
sock.bind((source_ip, broadcastPort))

frame_height = 0
row_count = 0
in_data = bytes()
compressed_length = 0
while True:
    try:
        buf, addr = sock.recvfrom(2048)
        #print("buf length=", len(buf))
        if compressed_length == 0 and len(buf) < 100:
            try:
                #print("buf length=", len(buf))
                header = buf.decode("utf-8")
                #print("Header:", header)
                if header[0] == 'f' and header[1] == 'm':
                    items = header.split(':')
                    #print(items)
                    frame_height = int(items[1])
                    #print("height=", frame_height)
                    compressed_length = int(items[4])
                    #print("compressed_length=", compressed_length)
                    row_count = 0
                    in_data = bytes()
            except Exception as e:
                print(e)
        else:
            if compressed_length > 0:
                in_data += buf
                if len(in_data) == compressed_length:
                    try:
                        #print("compressed_length=", compressed_length, "in_data length=", len(in_data), " buf length=",len(buf))
                        data_out = zlib.decompress( in_data)
                        #print("data_out length=", len(data_out))
                        deserialized_bytes = np.frombuffer(data_out, dtype=np.uint8)
                        frame = deserialized_bytes.reshape((480,640,3))
                        cv2.imshow('remote', frame)
                    except Exception as e:
                        print(e)
                    # Note!! must call waitKey or imshow cannot work fine
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:
                        break

                    in_data = bytes()
                    compressed_length = 0
                elif len(in_data) > compressed_length:
                    # data transfer error
                    in_data = bytes()
                    compressed_length = 0
            '''
            if frame_height > 0:
                in_data += buf
                row_count += 1
                if frame_height == row_count:
                    if len(in_data) == 480 * 640 * 3:
                        deserialized_bytes = np.frombuffer(in_data, dtype=np.uint8)
                        frame = deserialized_bytes.reshape((480,640,3))
                        cv2.imshow('remote', frame)
                        # Note!! must call waitKey or imshow cannot work fine
                        k = cv2.waitKey(1) & 0xFF
                        if k == 27:
                            break
                    
                    in_data = bytes()
                    frame_height = 0
            '''
            
        #print("recvfrom:", addr)
        #print("buf length:", len(buf))
    except Exception as e:
        print(e)
        break

sock.close()
#cap.release()
cv2.destroyAllWindows()
