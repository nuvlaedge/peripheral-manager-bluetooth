#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""NuvlaBox Peripheral Manager Bluetooth

This service provides bluetooth device discovery.

"""


import bluetooth
from bluetooth.ble import DiscoveryService
import logging
import requests
import sys
import time
from threading import Event
import os
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
    """ Simply waits for the NuvlaBox to finish bootstrapping, by pinging the Agent API
    :returns
    """

    logging.info("Checking if NuvlaBox has been initialized...")

    r = requests.get(healthcheck_endpoint)
    
    while not r.ok:
        time.sleep(5)
        r = requests.get(healthcheck_endpoint)

    logging.info('NuvlaBox has been initialized.')
    return

def send(url, assets):
    """ Sends POST request for registering new peripheral """

    logging.info("Sending GPU information to Nuvla")
    return publish(url, assets)


def bluetoothCheck(api_url, currentNetwork):
    """ Checks if peripheral already exists """

    logging.info('Checking if Bluetooth Device is already published')

    get_ethernet = requests.get(api_url + '?identifier_pattern=' + current_network['identifier'])
    
    logging.info(get_ethernet.json())

    if not get_ethernet.ok or not isinstance(get_ethernet.json(), list) or len(get_ethernet.json()) == 0:
        logging.info('Bluetooth Device hasnt been published.')
        return True
    
    elif get_ethernet.json() != currentNetwork:
        logging.info('Network has changed')
        return True

    logging.info('Bluetooth device has already been published.')
    return False


def publish(url, assets):
    """
    API publishing function.
    """

    x = requests.post(url, json=assets)
    return x.json()


def deviceDiscovery():
    """
    Return all discoverable bluetooth devices.
    """
    return bluetooth.discover_devices(lookup_names=True)


def bleDeviceDiscovery():
    service = DiscoveryService()
    devices = service.discover(2)
    return devices


def bluetoothManager():

    output = []

    try:
        bluetoothDevices = deviceDiscovery()
        bleDevices = bleDeviceDiscovery()
        for device in bluetoothDevices:
            output.append({
                    "available": True,
                    "name": device[1],
                    "classes": ["computer", "audio", "video", "tv", ...],
                    "identifier": device[0],
                    "interface": "bluetooth",
            })
    except:
        output = {
                "available": False,
                "interface": "bluetooth",
        }

    return output
    

if __name__ == "__main__":

    init_logger()

    API_BASE_URL = "http://agent/api"

    wait_bootstrap()

    API_URL = API_BASE_URL + "/peripheral"

    e = Event()

    while True:

        current_network = bluetoothManager()

        if current_network:
            for i in current_network:
                peripheral_already_registered = bluetoothCheck(API_URL, i)

                if peripheral_already_registered:
                    send(API_URL, i)

        e.wait(timeout=90)


