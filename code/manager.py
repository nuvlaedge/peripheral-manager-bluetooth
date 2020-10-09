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
import docker
from packaging import version
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


def wait_bootstrap(context_file):
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

    logging.info('NuvlaBox has been initialized.')
    return


def bluetoothCheck(api_url, currentDevices):
    """ Checks if peripheral already exists """

    logging.info('Checking if Bluetooth Device is already published')

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

    logging.info('Bluetooth device has already been published.')
    return False
    

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
    except:
        bluetoothDevices = []

    try:
        bleDevices = bleDeviceDiscovery()
    except:
        bleDevices = []

    bluetooth = compareBluetooth(bluetoothDevices, bleDevices)
    if len(bluetooth) > 0:
        for device in bluetooth:
            output[device[0][0]] = {
                    "parent": nuvlabox_id,
                    "version": nuvlabox_version,
                    "available": True,
                    "name": device[0][1],
                    "classes": [],
                    "identifier": device[0][0],
                    "interface": device[-1],
                }
    print(output)
    return output


def add(data, api_url, activated_path, cookies_file):

    api = Api(api_url)

    activated = json.load(open(activated_path))
    api_key = activated['api-key']
    secret_key = activated['secret-key']
    
    login = api.login_apikey(api_key, secret_key)

    if login.status_code == 201 or login.status_code == 200:
        response = api.add('nuvlabox-peripheral', data).data
        if response['status'] == 200:
            return response['resource-id']
        else:
            return ''
    else:
        return ''


def remove(resource_id, api_url, activated_path, cookies_file):
    
    api = Api(api_url)

    activated = json.load(open(activated_path))
    api_key = activated['api-key']
    secret_key = activated['secret-key']
    
    login = api.login_apikey(api_key, secret_key)

    if login.status_code == 201 or login.status_code == 200:
        response = api.delete(resource_id).data
        if response['status'] == 200:
            return response['resource-id']
        else:
            return ''
    else:
        return ''

if __name__ == "__main__":

    activated_path = '/home/quietswami/nuvlabox/shared/.activated'
    context_path = '/home/quietswami/nuvlabox/shared/.context'
    cookies_file = '/home/quietswami/nuvlabox/shared/cookies'

    context = json.load(open(context_path))

    version = context['version']
    nuvlabox_id = context['id']

    print('BLUETOOTH MANAGER STARTED')

    init_logger()

    API_BASE_URL = "https://nuvla.io"

    # wait_bootstrap()

    API_URL = API_BASE_URL + "/peripheral"

    # e = Event()

    devices = {}
    
    while True:

        current_devices = bluetoothManager(nuvlabox_id, version)
        print('CURRENT DEVICES: {}\n'.format(current_devices), flush=True)
        
    #     if current_devices != devices and current_devices:

    #         devices_set = set(devices.keys())
    #         current_devices_set = set(current_devices.keys())

    #         publishing = current_devices_set - devices_set
    #         removing = devices_set - current_devices_set

    #         for device in publishing:

    #             peripheral_already_registered = \
    #                 bluetoothCheck(API_URL, current_devices[device])

    #             if not peripheral_already_registered:
    #                 print('PUBLISHING: {}'.format(current_devices[device]), flush=True)
    #                 resource_id = add(testPut, 'https://nuvla.io', activated_path, cookies_file)
    #                 devices[device] = {'resource_id': resource_id, 'message': current_devices[device]}

    #         for device in removing:

    #             peripheral_already_registered = \
    #                 bluetoothCheck(API_URL, devices[device])

    #             if peripheral_already_registered:
    #                 print('REMOVING: {}'.format(devices[device]), flush=True)
    #                 remove(API_URL, devices[device]['resource_id'])
    #                 del devices[device]

    #     e.wait(timeout=90)
