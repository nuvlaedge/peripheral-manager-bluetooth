#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""NuvlaBox Peripheral Manager Bluetooth
This service provides bluetooth device discovery.
"""

import bluetooth
from gattlib import DiscoveryService  # Used for BLE discovery
import logging
import requests
import sys
import time
from threading import Event
import json
from nuvla.api import Api
import os


def init_logger():
    """ Initializes logging """

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def wait_bootstrap(context_file, base_peripheral_path, peripheral_path):
    """
    Waits for the NuvlaBox to finish bootstrapping, by checking
        the context file.
    :returns
    """
    is_context_file = False

    while not is_context_file:
        time.sleep(5)
        if os.path.isfile(context_file):
            is_context_file = True
            logging.info('Context file found')
        logging.info('Waiting for context file')

    peripheral = False

    if not os.path.isdir(peripheral_path):
        while not peripheral:
            logging.info('Wating for peripheral directory...')
            if os.path.isdir(base_peripheral_path):
                os.mkdir(peripheral_path)
                peripheral = True
                logging.info('PERIPHERAL: {}'.format(peripheral))

    logging.info('NuvlaBox has been initialized.')
    return


def bluetoothCheck(peripheral_dir, mac_addr):
    """ Checks if peripheral already exists """
    print('PATH: {}'.format(peripheral_dir))
    print('MAC ADDR: {}'.format(mac_addr))
    if mac_addr in os.listdir(peripheral_dir):
        return True
    return False


def createDeviceFile(device_mac_addr, device_file, peripheral_dir):

    file_path = '{}/{}'.format(peripheral_dir, device_mac_addr)

    with open(file_path, 'w') as outfile:
        json.dump(device_file, outfile)


def removeDeviceFile(device_mac_addr, peripheral_dir):
    file_path = '{}/{}'.format(peripheral_dir, device_mac_addr)

    os.unlink(file_path)


def readDeviceFile(device_mac_addr, peripheral_dir):
    file_path = '{}/{}'.format(peripheral_dir, device_mac_addr)

    return json.load(open(file_path))


def deviceDiscovery():
    """
    Return all discoverable bluetooth devices.
    """
    return bluetooth.discover_devices(lookup_names=True)


def bleDeviceDiscovery():
    service = DiscoveryService("hci0")
    devices = list(service.discover(2).items())
    return devices


def compareBluetooth(bluetooth, ble):
    output = []

    for device in bluetooth:
        if device not in ble:
            output.append((device, 'bluetooth'))

    for device in ble:
        output.append((device, 'bluetooth-le'))

    return output


def bluetoothManager(nuvlabox_id, nuvlabox_version):

    output = {}

    try:
        bluetoothDevices = deviceDiscovery()
        print(bluetoothDevices)
    except:
        bluetoothDevices = []

    try:
        bleDevices = bleDeviceDiscovery()
        print(bleDevices)
    except:
        bleDevices = []

    bluetooth = compareBluetooth(bluetoothDevices, bleDevices)
    if len(bluetooth) > 0:
        for device in bluetooth:
            name = "Unknown" if device[0][1] == "" else device[0][1]
            output[device[0][0]] = {
                    "parent": nuvlabox_id,
                    "version": nuvlabox_version,
                    "available": True,
                    "name": name,
                    "classes": [],
                    "identifier": device[0][0],
                    "interface": device[-1],
                }

    return output


def add(data, api_url, activated_path, cookies_file):

    api = Api(api_url)

    activated = json.load(open(activated_path))
    api_key = activated['api-key']
    secret_key = activated['secret-key']
    
    api.login_apikey(api_key, secret_key)

    response = api.add('nuvlabox-peripheral', data).data
    return response['resource-id']


def remove(resource_id, api_url, activated_path, cookies_file):
    print('REMOVING FROM NUVLA: {}'.format(resource_id))
    api = Api(api_url)

    activated = json.load(open(activated_path))
    api_key = activated['api-key']
    secret_key = activated['secret-key']
    
    api.login_apikey(api_key, secret_key)

    response = api.delete(resource_id).data
    return response['resource-id']


def diff(before, after):
    enter = []
    leaving = []

    for key in before.keys():
        if key not in after.keys():
            leaving.append(key)
    
    for key in after.keys():
        if key not in before.keys():
            enter.append(key) 

    return enter, leaving

if __name__ == "__main__":

    activated_path = '/srv/nuvlabox/shared/.activated'
    context_path = '/srv/nuvlabox/shared/.context'
    cookies_file = '/srv/nuvlabox/shared/cookies'
    base_peripheral_path = '/srv/nuvlabox/shared/.peripherals/'
    peripheral_path = '/srv/nuvlabox/shared/.peripherals/bluetooth'

    print('BLUETOOTH MANAGER STARTED')

    init_logger()

    API_URL = "https://nuvla.io"

    wait_bootstrap(context_path, base_peripheral_path, peripheral_path)

    context = json.load(open(context_path))

    NUVLABOX_VERSION = context['version']
    NUVLABOX_ID = context['id']

    e = Event()

    devices = {}
    
    while True:

        current_devices = bluetoothManager(NUVLABOX_ID, NUVLABOX_VERSION)
        print('CURRENT DEVICES: {}\n'.format(current_devices), flush=True)
        
        if current_devices != devices and current_devices:

            print('DEVICES: {}'.format(devices))

            publishing, removing = diff(devices, current_devices)
            
            print('Publishing: {}'.format(publishing))
            print('Removing: {}'.format(removing))

            for device in publishing:

                peripheral_already_registered = \
                    bluetoothCheck(peripheral_path, device)

                print('EXISTS: {}'.format(peripheral_already_registered))

                resource_id = ''

                if not peripheral_already_registered:

                    print('PUBLISHING: {}'.format(current_devices[device]), flush=True)
                    resource_id = add(current_devices[device], 'https://nuvla.io', activated_path, cookies_file)

                devices[device] = {'resource_id': resource_id, 'message': current_devices[device]}
                createDeviceFile(device, devices[device], peripheral_path)
                print('POS APPEND DEVICES: {}'.format(devices))

            for device in removing:
                
                print('REMOVING: {}'.format(devices[device]))

                peripheral_already_registered = \
                    bluetoothCheck(peripheral_path, device)
                
                print(peripheral_already_registered)

                if peripheral_already_registered:

                    print('REMOVING: {}'.format(devices[device]), flush=True)
                    
                    read_file = readDeviceFile(device, peripheral_path)

                    print(read_file)
                    
                    remove(read_file['resource_id'], API_URL, activated_path, cookies_file)
                    removeDeviceFile(device, peripheral_path)
                
                del devices[device]

        e.wait(timeout=90)
