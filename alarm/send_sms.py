# -*- coding: utf-8 -*-
#
# Sending a SMS with Python and pyserial via an USB 3G Modem on pfSense/FreeBSD
# tested with: Huawei Technologies Co., Ltd. E620 USB Modem
# and a Telekom SIM card
import glob
import serial
import time
import sys
import getopt
import argparse

def get_serial_port():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    for port in ports:
        try:
            s = serial.Serial(port)
            s.write(b'AT+CGMI\r')
            s.timeout = 1
            sent_cmd = s.readline()
            response = s.readline().decode("utf-8")
            s.close()
            if response.startswith("huawei"):
                return port
        except (OSError, serial.SerialException):
            pass

def send_sms(message, phonenumber):
    baudrate = 9600
    device = get_serial_port()
    # Initialize serial connection to 3G USB Modem
    modem = serial.Serial(device, baudrate, timeout=1)
    print("Connected to " + modem.name)
    # Check modem status
    modem.write(b'AT\r')
    sent_cmd = modem.readline()
    response = modem.read(4).decode("utf-8")
    if "OK" in response:
        print("Modem Status: OK")
        # check pin and enter it if needed
        modem.write(b'AT+CPIN?\r')
        sent_cmd = modem.readline()
        line2 = modem.readline()  # empty
        line3 = modem.readline()  # empty
        response = modem.readline().decode("utf-8")  # get OK
        if "SIM PIN" in response:
            print("Sending PIN to modem ... ")
            modem.write(b'AT+CPIN="%s"' % simpin)
            sent_cmd = modem.readline()
            response = modem.readline().decode("utf-8")
            print(response)
        elif "READY" in response:
            print("PIN already entered.")
        # set modem to text mode
        modem.write(b'AT+CMGF=1\r')
        sent_cmd = modem.readline()
        response = modem.readline().decode("utf-8")
        if "OK" in response:
            print("Modem set to text mode!")
            # send sms
            print("Sending sms ...")
            modem.write(b'AT+CMGS="%s"\r' % phonenumber)
            time.sleep(0.5)
            modem.write(b'%s\r' % message)
            time.sleep(0.5)
            modem.write(chr(26).encode("utf-8"))
            time.sleep(0.5)
            response = modem.readlines()
            if "+CMGS" in response[-3].decode("utf-8"):
                print("Sucess: SMS sent!")
            else:
                print("Error: SMS not sent!")
        else:
            print("Error: Setting modem to text mode failed!")
    elif "NO CARRIER" in response:
        print("Error: No 3G connection!")
    else:
        print("Error: Something else failed!")


parser = argparse.ArgumentParser(description='Sending messages.')
parser.add_argument('--message', type=str, help='SMS message', required=True)
parser.add_argument('--number', type=str, help='SMS receiver number', required=True)
args = parser.parse_args()

send_sms(args.message.encode("utf-8"), args.number.encode("utf-8"))