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

def read_sms():
    baudrate = 9600
    device = get_serial_port()
    # Initialize serial connection to 3G USB Modem
    modem = serial.Serial(device, baudrate, timeout=1)
    print("Connected to " + modem.name)
    # Check modem status
    modem.write(b'AT+CMGL="REC READ"\r')
    sent_cmd = modem.readline()
    response = modem.readlines()
    if "OK" in response[0].decode("utf-8"):
        print("No new messages")
        return ""
    for line in response:
        linestr = line.decode("utf-8")
        if linestr.startswith("+CMGL"):
            print(linestr)


read_sms()