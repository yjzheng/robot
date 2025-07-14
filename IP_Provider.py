import time
import subprocess
import socket
import argparse

def get_ether_id():
    string = ""
    out = subprocess.Popen(['ifconfig'], 
               stdout=subprocess.PIPE, 
               stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    #print(stdout, type(stdout))
    words = stdout.split(b'\n')
    try:
        search1 = b'wlan0'
        search2 = 'ether '
        for index in range(len(words)):
            #print(words[index])
            if search1 == words[index][:len(search1)]:
                index += 1
                while index < len(words):
                    string = str(words[index]) # get next line
                    #print("string:"+string)
                    sub_index = string.find(search2)
                    if sub_index != -1:
                        string = string[sub_index + len(search2):]
                        string = string[:string.find(' ')]
                        #print(string)
                        break
                    index += 1
                break
        #print(stderr)
    except:
        pass
    return string

def get_ip_address():
    string = ""
    out = subprocess.Popen(['ifconfig'], 
               stdout=subprocess.PIPE, 
               stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    #print(stdout, type(stdout))
    words = stdout.split(b'\n')
    try:
        search1 = b'wlan0'
        search2 = 'inet '
        for index in range(len(words)):
            #print(words[index])
            if search1 == words[index][:len(search1)]:
                string = str(words[index+1]) # get next line
                sub_index = string.find(search2)
                string = string[sub_index + len(search2):]
                string = string[:string.find(' ')]
                #print(string)
                break
        #print(stderr)
    except:
        pass
    return string
etherID = ""
ip = ""
while True:
    etherID = get_ether_id()
    print("ether:", etherID)
    ip = get_ip_address()
    print("ip:", ip)
    if len(ip) > 0:
        break
    time.sleep(1)

queryPort = 55051
responsePort = 55052

source_ip="0.0.0.0"
source_port=queryPort

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # SOCK_DGRAM for UDP
sock.settimeout(None) # Set a timeout on blocking socket operations. blocking mode
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state
sock.bind((source_ip, source_port))

while True:
    try:
        buf, addr = sock.recvfrom(2048)
        print("recvfrom:", addr)
        print("buf:", buf)
        if len(buf) > 0:
            applyEtherID = buf.decode('utf-8')
            if applyEtherID == etherID:
                print("Matched!")
                sock.sendto(bytes(ip, "utf-8"), (addr[0], responsePort))
        received = True
    except KeyboardInterrupt:
        break
    except Exception:
        received = False
        break

print("close")
sock.close()
