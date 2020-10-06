#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""NuvlaBox Peripheral Manager Bluetooth
This service provides bluetooth device discovery.
"""


<<<<<<< HEAD
import bluetooth 
from gattlib import DiscoveryService # Used for BLE discovery
=======
import bluetooth
from gattlib import DiscoveryService  # Used for BLE discovery
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795
import logging
import requests
import sys
import time
from threading import Event
import json


def init_logger():
    """ Initializes logging """

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def wait_bootstrap(healthcheck_endpoint="http://agent/api/healthcheck"):
    """
    Simply waits for the NuvlaBox to finish bootstrapping, by pinging
        the Agent API
    :returns
    """

    logging.info("Checking if NuvlaBox has been initialized...")

    r = requests.get(healthcheck_endpoint)

    while not r.ok:
        time.sleep(5)
        r = requests.get(healthcheck_endpoint)

    logging.info('NuvlaBox has been initialized.')
    return


def publish(url, assets):
    """
    API publishing function.
    """

    x = requests.post(url, json=assets)
    return x.json()


def send(url, assets):
    """ Sends POST request for registering new peripheral """

    logging.info("Sending Bluetooth Device information to Nuvla")
    return publish(url, assets)


def remove(url, assets):
    logging.info("Removing Bluetooth Device from Nuvla")
    x = requests.delete(url, json=assets)
    return x.json()

<<<<<<< HEAD
def bluetoothCheck(api_url, currentNetwork):
=======

def bluetoothCheck(api_url, currentDevices):
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795
    """ Checks if peripheral already exists """

    logging.info('Checking if Bluetooth Device is already published')

<<<<<<< HEAD
    get_ethernet = requests.get(api_url + '?identifier_pattern=' + currentNetwork['identifier'])
    
    logging.info(get_ethernet.json())

    if not get_ethernet.ok or not isinstance(get_ethernet.json(), list) or len(get_ethernet.json()) == 0:
        logging.info('Bluetooth Device hasnt been published.')
        return True
    
    elif get_ethernet.json() != currentNetwork:
        logging.info('Network has changed')
        return True
=======
    get_bluetooth = requests.get(api_url + '?identifier_pattern=' +
                                currentDevices['identifier'])

    logging.info(get_bluetooth.json())

    if not get_bluetooth.ok or \
        not isinstance(get_bluetooth.json(), list) \
            or len(get_bluetooth.json()) == 0:

        logging.info('Bluetooth Device hasnt been published.')
        return False

    elif get_bluetooth.json() != currentDevices:
        logging.info('Network has changed')
        return False
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795

    logging.info('Bluetooth device has already been published.')
    return False


def deviceDiscovery():
    """
    Return all discoverable bluetooth devices.
    """
<<<<<<< HEAD
    return bluetooth.discover_devices(lookup_names=True, lookup_class=True)


def bleDeviceDiscovery():
    
=======
    return bluetooth.discover_devices(lookup_names=True)


def bleDeviceDiscovery():
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795
    service = DiscoveryService("hci0")
    devices = list(service.discover(2).items())
    return devices


def compareBluetooth(bluetooth, ble):
    output = []

    for device in bluetooth:
        if device not in ble:
<<<<<<< HEAD
            a = (device, 'bluetooth')
            if len(device) > 2:
                c = converter.convert(str(device[-1]))
                a = (device, 'bluetooth', c)
            output.append(a)
=======
            output.append((device, 'bluetooth'))
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795

    for device in ble:
        output.append((device, 'bluetooth-le'))

    return output

<<<<<<< HEAD
def bluetoothManager():

    output = []
=======

def bluetoothManager():

    output = {}
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795

    try:
        bluetoothDevices = deviceDiscovery()
    except:
<<<<<<< HEAD
        logging.info('BLUETOOTH NOT AVAILABLE')
        bluetoothDevices = []
    try:
        bleDevices = bleDeviceDiscovery()
    except:
        logging.info('BLE NOT AVAILABLE')
        bleDevices = []
    
    bluetooth = compareBluetooth(bluetoothDevices, bleDevices)

    if len(bluetooth) != 0:
        for device in bluetooth:

            d = {
                "available": True,
                "name": device[0][1],
                "classes": [],
                "identifier": device[0][0],
                "interface": device[1],
            }

            if len(device) > 2:
                d['classes'] = device[-1]
            
            output.append(d)

    return output
    
=======
        bluetoothDevices = []

    try:
        bleDevices = bleDeviceDiscovery()
    except:
        bleDevices = []

    bluetooth = compareBluetooth(bluetoothDevices, bleDevices)
    if len(bluetooth) > 0:
        for device in bluetooth:
            output[device[0][0]] = {
                    "available": True,
                    "name": device[0][1],
                    "classes": [],
                    "identifier": device[0][0],
                    "interface": device[-1],
                }

    return output

>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795

if __name__ == "__main__":

    print('BLUETOOTH MANAGER STARTED')

    init_logger()

    API_BASE_URL = "http://agent/api"

    # wait_bootstrap()

    API_URL = API_BASE_URL + "/peripheral"

    # e = Event()

<<<<<<< HEAD
    network = []

    while True:

        current_network = bluetoothManager()

        if current_network and current_network != network and current_network != []:

            for device in current_network:

                device_json = json.dumps(device)
                
                # peripheral_already_registered = bluetoothCheck(API_URL, device_json)

                if device not in network:
                    # send(API_URL, device_json)
                    print('PUBLISHING: {}'.format(device))
                
                elif device in network:
                    # remove(API_URL, device_json)
                    print('REMOVING" {}'.format(device))
            
            network = current_network
            print('CURRENT NETWORK: {}'.format(network))
        # e.wait(timeout=90)
=======
    devices = {}

    while True:

        current_devices = bluetoothManager()
        print('CURRENT DEVICES: {}'.format(current_devices))
        
        if current_devices != devices and current_devices:

            devices_set = set(devices.keys())
            current_devices_set = set(current_devices.keys())

            publishing = current_devices_set - devices_set
            removing = devices_set - current_devices_set

            for device in publishing:

                # peripheral_already_registered = \
                    # bluetoothCheck(API_URL, current_devices[device])

                # if not peripheral_already_registered:
                print('PUBLISHING: {}'.format(current_devices[device]))
                    # send(API_URL, current_devices[device])
                    # devices[device] = current_devices[device]

            for device in removing:

                # peripheral_already_registered = \
                    # bluetoothCheck(API_URL, devices[device])
>>>>>>> 333e1985393935167c77ad301d7e6b5bffff6795

                # if peripheral_already_registered:
                print('REMOVING: {}'.format(devices[device]))
                    # remove(API_URL, devices[device])
                    # del devices[device]

        # e.wait(timeout=90)
