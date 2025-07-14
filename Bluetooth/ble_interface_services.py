import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from advertisement import Advertisement
from advertisement import register_ad_cb, register_ad_error_cb
from gatt_server import Service, Characteristic
from gatt_server import register_app_cb, register_app_error_cb
import subprocess

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

def wifi_connect( ssid, password):
    ret_str = ""
    cmd = "sudo iwlist wlan0 scanning"
    out = subprocess.Popen(cmd, shell= True,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
    stdout,stderr = out.communicate()
    if len(stderr) != 0:
        ret_str = stderr.decode()
    else :
        ret_str = stdout.decode()
    print("ret_str=", ret_str)

    cmd = 'sudo nmcli dev wifi connect "' + ssid + '" password "' + password + '"'
    #cmd = ["nmcli", "dev", "wifi", "connect", '"'+ssid+'"', "password", '"'+ password + '"']
    print("cmd:", cmd)
    try:
        out = subprocess.Popen(cmd, shell= True,
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        stdout,stderr = out.communicate()
        if len(stderr) != 0:
            ret_str = stderr.decode()
        else :
            ret_str = stdout.decode()
    except Exception as e:
        print("e:", e)
    print("ret_str=", ret_str)
    return ret_str

global timeout_return

def my_timeout_function():
    print("Timeout function called!")
    process = subprocess.Popen("bluetoothctl pairable off", shell=True)

    # Return True to repeat the timeout, False to stop it
    return timeout_return 

BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
#LOCAL_NAME =                   'rpi-gatt-server'
LOCAL_NAME =                   'Robot V1.0'
mainloop = None
quit_request = False

class TxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify','read'], service)
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)

    def on_console_input(self, fd, condition):
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True

    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False

    def ReadValue(self, options):
        value = []
        data_str = self.service.get_result()
        print("ReadValue:data_str:",data_str)
        for c in data_str:
            value.append(dbus.Byte(c.encode()))
        return value
    
class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)

    def WriteValue(self, value, options):
        input_str = bytearray(value).decode()
        print('remote: {}'.format(input_str))
        self.service.set_input_data(input_str)

class UartService(Service):
    def __init__(self, bus, index):
        self.input_data = ""
        self.output_data = ""
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.add_characteristic(TxCharacteristic(bus, 0, self))
        self.add_characteristic(RxCharacteristic(bus, 1, self))
    
    def set_input_data(self, data_string):
        self.input_data = data_string
        global timeout_return
        timeout_return = GLib.SOURCE_REMOVE
        print("input_data:", data_string)
        if data_string == "EXIT" :
            print("Quit request!")
            quit_request = True
            mainloop.quit()
            #GLib.g_main_loop_quit(mainloop)
        elif data_string == "SHUTDOWN":
            subprocess.Popen("sudo shutdown now", shell=True)
        elif data_string == "GEID":
            self.output_data = get_ether_id()
        elif data_string == "GIP":
            self.output_data = get_ip_address()
        elif data_string[0] == 'S':
            items = data_string.split(':')
            if len(items) == 3 and items[0] == "SWF":
                self.output_data = wifi_connect( items[1], items[2])
        print("output_data:", self.output_data)

    def get_result(self):
        print(">>get_result,data length:", len(self.output_data))
        return self.output_data

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)

    def get_path(self):
        return dbus.ObjectPath(self.path)

    def add_service(self, service):
        self.services.append(service)

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
        return response

class UartApplication(Application):
    def __init__(self, bus):
        Application.__init__(self, bus)
        self.add_service(UartService(bus, 0))

class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                               DBUS_OM_IFACE)
    objects = remote_om.GetManagedObjects()
    for o, props in objects.items():
        if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
            return o
        print('Skip adapter:', o)
    return None

import time
import RPi.GPIO as GPIO
CHECK_PIN1 = 38
CHECK_PIN2 = 40

def check_active_need():
    yes = False
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(CHECK_PIN1, GPIO.OUT)
    GPIO.setup(CHECK_PIN2, GPIO.IN)
    GPIO.output(CHECK_PIN1, True )
    time.sleep(0.2)
    if GPIO.input( CHECK_PIN2) == True:
        GPIO.output(CHECK_PIN1, False )
        time.sleep(0.2)
        if GPIO.input( CHECK_PIN2) == False:
            yes = True
        
    return yes

def main():
    if check_active_need() == False:
        print("No active need.")
        return
    
    global mainloop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    adapter = find_adapter(bus)
    if not adapter:
        print('BLE adapter not found')
        return

    service_manager = dbus.Interface(
                                bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                LE_ADVERTISING_MANAGER_IFACE)

    app = UartApplication(bus)
    adv = UartAdvertisement(bus, 0)

    mainloop = GLib.MainLoop()

    global timeout_return
    timeout_return = GLib.SOURCE_CONTINUE
    GLib.timeout_add(3000, my_timeout_function)

    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)
    ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass
    adv.Release()

if __name__ == '__main__':
    main()
