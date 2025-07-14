# USAGE: python SendUDP.py -b 0 -i 192.168.50.127 -p 54320 -d "ABCDE"
# USAGE: python SendUDP.py -b 1 -p 54320 -d "HI"
import socket
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('--data2send', '-d', type=str, default="", required=False, help='The data send to target.')
args = parser.parse_args()

ether_address = ""
if args.data2send == "":
    ether_address = input("Input Ethernet Address:")
else:
    ether_address = args.data2send

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)    # SOCK_DGRAM for UDP
sock.settimeout(1) # Set a timeout on blocking socket operations. 1 seconds
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state

sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
host = "255.255.255.255"

queryPort = 55051
responsePort = 55052

source_ip="0.0.0.0"
sock.bind((source_ip, responsePort))

for i in range(60):
    print("sendto:",host,queryPort)
    sock.sendto(bytes(ether_address, "utf-8"), (host, queryPort))

    try:
        buf, addr = sock.recvfrom(2048)
        print("recvfrom:", addr)
        print("buf:", buf)
        break
    except Exception:
        pass

sock.close()