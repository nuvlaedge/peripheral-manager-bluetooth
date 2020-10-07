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
>>>>>>> 6c2823b0baac7a533f2e97d1b2925be18b8f8d19
import logging
import requests
import sys
import time
from threading import Event
import json
import docker
from packaging import version
import nuvla

image = 'bluetooth_information:{}'


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
    

def getCurrentImageVersion(client):

    peripheralVersion = ''
    bluetoothVersion = ''
    
    for container in client.containers.list():
        img, tag = container.image.attrs['RepoTags'][0].split(':')
        if img == 'nuvlabox/peripheral-manager-bluetooth':
            peripheralVersion = tag
        elif img == image:
            bluetoothVersion = tag

    if version.parse(peripheralVersion) > version.parse(bluetoothVersion):
        return peripheralVersion

    else:
        return '0.0.1'


def launchSideContainer():
    client = docker.from_env()
    volumes = {}

    currentVersion = getCurrentImageVersion(client)
    img = image.format(currentVersion)

    dbus = '/var/run/dbus'
    volumes[dbus] = {'bind': dbus, 'mode': 'ro'}

    if len(client.images.list(img)) == 0 and currentVersion != '':
        logging.info('Build CUDA Cores Image')
        client.images.build(path='.', tag=img, dockerfile='Dockerfile.bluetooth')

    output = client.containers.run(img, network_mode="host", volumes=volumes)
    print('OUTPUT: {}'.format(output))
    return output

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


def bluetoothManager():

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
                    "available": True,
                    "name": device[0][1],
                    "classes": [],
                    "identifier": device[0][0],
                    "interface": device[-1],
                }
    print(output)
    return output


if __name__ == "__main__":

    print('BLUETOOTH MANAGER STARTED')

    init_logger()

    API_BASE_URL = "http://agent/api"

    # wait_bootstrap()

    API_URL = API_BASE_URL + "/peripheral"

    # e = Event()

    devices = {}

    while True:
<<<<<<< HEAD
        
        print('Starting Search')
        current_network = launchSideContainer()
        print('Search Done')
        if current_network != network and current_network != []:
=======

        current_devices = bluetoothManager()
        print('CURRENT DEVICES: {}\n'.format(current_devices), flush=True)
        
        if current_devices != devices and current_devices:

            devices_set = set(devices.keys())
            current_devices_set = set(current_devices.keys())
>>>>>>> 6c2823b0baac7a533f2e97d1b2925be18b8f8d19

            publishing = current_devices_set - devices_set
            removing = devices_set - current_devices_set

            for device in publishing:

<<<<<<< HEAD
                print('PUBLISHING: {}'.format(current_network[device]))
                # peripheral_already_registered = bluetoothCheck(API_URL, current_network[device])

                # if peripheral_already_registered:
                    # send(API_URL, current_network[device])
                network[device] = current_network[device]

            for device in removing:

                print('REMOVING: {}'.format(network[device]))
                # peripheral_already_registered = bluetoothCheck(API_URL, network[device])
                
                # if not peripheral_already_registered:
                    # remove(API_URL, network[device])
                del network[device]

        # e.wait(timeout=90)
=======
                peripheral_already_registered = \
                    bluetoothCheck(API_URL, current_devices[device])

                if not peripheral_already_registered:
                    print('PUBLISHING: {}'.format(current_devices[device]), flush=True)
                    send(API_URL, current_devices[device])
                    devices[device] = current_devices[device]

            for device in removing:

                peripheral_already_registered = \
                    bluetoothCheck(API_URL, devices[device])

                if peripheral_already_registered:
                    print('REMOVING: {}'.format(devices[device]), flush=True)
                    remove(API_URL, devices[device])
                    del devices[device]

        e.wait(timeout=90)
>>>>>>> 6c2823b0baac7a533f2e97d1b2925be18b8f8d19
