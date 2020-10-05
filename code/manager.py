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


def bluetoothCheck(api_url, currentNetwork):
    """ Checks if peripheral already exists """

    logging.info('Checking if Bluetooth Device is already published')

    get_ethernet = requests.get(api_url + '?identifier_pattern=' +
                                currentNetwork['identifier'])

    logging.info(get_ethernet.json())

    if not get_ethernet.ok or \
        not isinstance(get_ethernet.json(), list) \
            or len(get_ethernet.json()) == 0:

        logging.info('Bluetooth Device hasnt been published.')
        return True

    elif get_ethernet.json() != currentNetwork:
        logging.info('Network has changed')
        return True

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

    return output


if __name__ == "__main__":

    init_logger()

    API_BASE_URL = "http://agent/api"

    wait_bootstrap()

    API_URL = API_BASE_URL + "/peripheral"

    e = Event()

    network = {}

    while True:

        current_network = bluetoothManager()

        if current_network != network and current_network != []:

            network_set = set(network.keys())
            current_network_set = set(current_network.keys())

            publishing = current_network_set - network_set
            removing = network_set - current_network_set

            for device in publishing:

                print('PUBLISHING: {}'.format(current_network[device]))
                peripheral_already_registered = \
                    bluetoothCheck(API_URL, current_network[device])

                if peripheral_already_registered:
                    send(API_URL, current_network[device])
                    network[device] = current_network[device]

            for device in removing:

                print('REMOVING: {}'.format(network[device]))
                peripheral_already_registered = \
                    bluetoothCheck(API_URL, network[device])

                if not peripheral_already_registered:
                    remove(API_URL, network[device])
                    del network[device]

        e.wait(timeout=90)
