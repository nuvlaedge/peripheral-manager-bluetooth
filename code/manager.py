#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""NuvlaBox Peripheral Manager Bluetooth
This service provides bluetooth device discovery.
"""

import bluetooth as bt
import logging
import sys
import time
import os
import json
from nuvla.api import Api
from bluetooth.ble import DiscoveryService
from threading import Event


scanning_interval = 30


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
            time.sleep(5)
            logging.info('Waiting for peripheral directory...')
            if os.path.isdir(base_peripheral_path):
                os.mkdir(peripheral_path)
                peripheral = True
                logging.info('PERIPHERAL: {}'.format(peripheral))

    logging.info('NuvlaBox has been initialized.')
    return


def bluetoothCheck(peripheral_dir, mac_addr):
    """ Checks if peripheral already exists """
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
    return bt.discover_devices(lookup_names=True, lookup_class=True)


def bleDeviceDiscovery():
    service = DiscoveryService("hci0")
    devices = service.discover(2)
    return devices


def compareBluetooth(bluetooth, ble):
    output = []

    for device in bluetooth:
        if device[0] not in ble:
            d = {
                "identifier": device[0],
                "class": device[2],
                "interface": "bluetooth"
            }

            if device[1] != "":
                d["name"] = device[1]

            output.append(d)

    for device_id, device_name in ble.items():
        d = {
            "identifier": device_id,
            "class": "",    # TODO
            "interface": "bluetooth-le"
        }

        if device_name != "":
            d["name"] = device_name

        output.append(d)

    return output


def cod_converter(cod_decimal_string):
    """ From a decimal value of CoD, map and retrieve the corresponding major class of a Bluetooth device

    :param cod_decimal_string: numeric string corresponding to the class of device
    :return: list of class(es)
    """

    if not cod_decimal_string or cod_decimal_string == "":
        return []

    cod_decimal_string = int(cod_decimal_string)

    # Major CoDs
    classes = {'0': {'major': 'Miscellaneous',
                     'minor': {}},
               '1': {
                   'major': 'Computer',
                   'minor': {
                       'bitwise': False,
                       '0': 'Uncategorized',
                       '1': 'Desktop workstation',
                       '2': 'Server-class computer',
                       '3': 'Laptop',
                       '4': 'Handheld PC/PDA (clamshell)',
                       '5': 'Palm-size PC/PDA',
                       '6': 'Wearable computer (watch size)',
                       '7': 'Tablet'}
               },
               '2': {
                   'major': 'Phone',
                   'minor': {
                       'bitwise': False,
                       '0': 'Uncategorized',
                       '1': 'Cellular',
                       '2': 'Cordless',
                       '3': 'Smartphone',
                       '4': 'Wired modem or voice gateway',
                       '5': 'Common ISDN access'
                   }
               },
               '3': {
                   'major': 'LAN/Network Access Point',
                   'minor': {
                       'bitwise': False,
                       '0': 'Fully available',
                       '1': '1% to 17% utilized',
                       '2': '17% to 33% utilized',
                       '3': '33% to 50% utilized',
                       '4': '50% to 67% utilized',
                       '5': '67% to 83% utilized',
                       '6': '83% to 99% utilized',
                       '7': 'No service available'
                   }
               },
               '4': {
                   'major': 'Audio/Video',
                   'minor': {
                       'bitwise': False,
                       '0': 'Uncategorized',
                       '1': 'Wearable Headset Device',
                       '2': 'Hands-free Device',
                       '3': '(Reserved)',
                       '4': 'Microphone',
                       '5': 'Loudspeaker',
                       '6': 'Headphones',
                       '7': 'Portable Audio',
                       '8': 'Car audio',
                       '9': 'Set-top box',
                       '10': 'HiFi Audio Device',
                       '11': 'VCR',
                       '12': 'Video Camera',
                       '13': 'Camcorder',
                       '14': 'Video Monitor',
                       '15': 'Video Display and Loudspeaker',
                       '16': 'Video Conferencing',
                       '17': '(Reserved)',
                       '18': 'Gaming/Toy'
                   }
               },
               '5': {
                   'major': 'Peripheral',
                   'minor': {
                       'bitwise': False,
                       'feel': {
                           '0': 'Not Keyboard / Not Pointing Device',
                           '1': 'Keyboard',
                           '2': 'Pointing device',
                           '3': 'Combo keyboard/pointing device'
                       },
                       '0': 'Uncategorized',
                       '1': 'Joystick',
                       '2': 'Gamepad',
                       '3': 'Remote control',
                       '4': 'Sensing device',
                       '5': 'Digitizer tablet',
                       '6': 'Card Reader',
                       '7': 'Digital Pen',
                       '8': 'Handheld scanner for bar-codes, RFID, etc.',
                       '9': 'Handheld gestural input device'
                   }
               },
               '6': {
                   'major': 'Imaging',
                   'minor': {
                       'bitwise': True,
                       '4': 'Display',
                       '8': 'Camera',
                       '16': 'Scanner',
                       '32': 'Printer'
                   }
               },
               '7': {
                   'major': 'Wearable',
                   'minor': {
                       'bitwise': False,
                       '0': 'Wristwatch',
                       '1': 'Pager',
                       '2': 'Jacket',
                       '3': 'Helmet',
                       '4': 'Glasses'
                   }
               },
               '8': {
                   'major': 'Toy',
                   'minor': {
                       'bitwise': False,
                       '0': 'Robot',
                       '1': 'Vehicle',
                       '2': 'Doll / Action figure',
                       '3': 'Controller',
                       '4': 'Game'
                   }
               },
               '9': {
                   'major': 'Health',
                   'minor': {
                       'bitwise': False,
                       '0': 'Undefined',
                       '1': 'Blood Pressure Monitor',
                       '2': 'Thermometer',
                       '3': 'Weighing Scale',
                       '4': 'Glucose Meter',
                       '5': 'Pulse Oximeter',
                       '6': 'Heart/Pulse Rate Monitor',
                       '7': 'Health Data Display',
                       '8': 'Step Counter',
                       '9': 'Body Composition Analyzer',
                       '10': 'Peak Flow Monitor',
                       '11': 'Medication Monitor',
                       '12': 'Knee Prosthesis',
                       '13': 'Ankle Prosthesis',
                       '14': 'Generic Health Manager',
                       '15': 'Personal Mobility Device'
                   }
               }}

    major_number = (cod_decimal_string >> 8) & 0x1f
    minor_number = (cod_decimal_string >> 2) & 0x3f

    minor_class_name = None
    minor = {'minor': {}}
    if major_number == 31:
        major = {'major': 'Uncategorized'}
    else:
        major = classes.get(major_number, {'major': 'Reserved'})
        minor = classes.get(major_number, minor)

    minor_class = minor.get('minor', {})
    if minor_class.get('bitwise', False):
        # i.e. imaging
        for key, value in minor_class.items():
            try:
                # if key is an integer, it is good to be evaluated
                minor_key = int(key)
            except ValueError:
                continue
            except:
                logging.exception("Failed to evaluate minor device class with key %s" % key)
                continue

            if minor_number & minor_key:
                minor_class_name = value
                break
    else:
         minor_class_name = minor_class.get(str(minor_number), 'reserved')

    major_class_name = major.get('major')

    peripheral_classes = [major_class_name, minor_class_name]

    if 'feel' in minor_class:
        feel_number = minor_number >> 4
        feel_class_name = minor_class['feel'].get(str(feel_number))
        if feel_class_name:
            peripheral_classes.append(feel_class_name)

    return peripheral_classes


def bluetoothManager(nuvlabox_id, nuvlabox_version):

    output = {}

    try:
        # list
        bluetoothDevices = deviceDiscovery()
        logging.info(bluetoothDevices)
    except:
        bluetoothDevices = []
        logging.exception("Failed to discover BT devices")

    try:
        # dict
        bleDevices = bleDeviceDiscovery()
        logging.info(bleDevices)
    except:
        bleDevices = []
        logging.exception("Failed to discover BLE devices")

    # get formatted list of bt devices [{},...]
    bluetooth = compareBluetooth(bluetoothDevices, bleDevices)
    if len(bluetooth) > 0:
        for device in bluetooth:
            name = device.get("name", "unknown")
            output[device[0][0]] = {
                    "parent": nuvlabox_id,
                    "version": nuvlabox_version,
                    "available": True,
                    "name": name,
                    "classes": cod_converter(device.get("class", "")),
                    "identifier": device.get("identifier"),
                    "interface": device.get("interface", "bluetooth"),
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

    init_logger()
    logging.info('BLUETOOTH MANAGER STARTED')
    e = Event()

    activated_path = '/srv/nuvlabox/shared/.activated'
    context_path = '/srv/nuvlabox/shared/.context'
    cookies_file = '/srv/nuvlabox/shared/cookies'
    base_peripheral_path = '/srv/nuvlabox/shared/.peripherals/'
    peripheral_path = '/srv/nuvlabox/shared/.peripherals/bluetooth'

    API_URL = os.getenv("NUVLA_ENDPOINT", "nuvla.io")
    while API_URL[-1] == "/":
        API_URL = API_URL[:-1]

    API_URL = API_URL.replace("https://", "")

    wait_bootstrap(context_path, base_peripheral_path, peripheral_path)

    while True:
        try:
            with open(context_path) as c:
                context = json.loads(c.read())
            NUVLABOX_VERSION = context['version']
            NUVLABOX_ID = context['id']
            break
        except (json.decoder.JSONDecodeError, KeyError):
            logging.exception(f"Waiting for {context_path} to be populated")
            e.wait(timeout=5)

    old_devices = {}

    while True:

        current_devices = bluetoothManager(NUVLABOX_ID, NUVLABOX_VERSION)
        logging.info('CURRENT DEVICES: {}\n'.format(current_devices), flush=True)
        
        if current_devices != old_devices and current_devices:

            publishing, removing = diff(old_devices, current_devices)
            
            logging.info('Removing: {}'.format(removing))

            for device in publishing:

                peripheral_already_registered = bluetoothCheck(peripheral_path, device)

                resource_id = ''

                if not peripheral_already_registered:

                    logging.info('PUBLISHING: {}'.format(current_devices[device]), flush=True)
                    try:
                        resource_id = add(current_devices[device], API_URL, activated_path, cookies_file)
                    except:
                        logging.exception(f'Unable to publish peripheral {device}')

                old_devices[device] = {'resource_id': resource_id, 'message': current_devices[device]}
                createDeviceFile(device, old_devices[device], peripheral_path)

            for device in removing:
                
                logging.info('REMOVING: {}'.format(old_devices[device]))

                peripheral_already_registered = \
                    bluetoothCheck(peripheral_path, device)
                
                logging.info(peripheral_already_registered)

                if peripheral_already_registered:

                    logging.info('REMOVING: {}'.format(old_devices[device]), flush=True)
                    
                    read_file = readDeviceFile(device, peripheral_path)
                    
                    remove(read_file['resource_id'], API_URL, activated_path, cookies_file)
                    removeDeviceFile(device, peripheral_path)
                
                del old_devices[device]

        e.wait(timeout=scanning_interval)
