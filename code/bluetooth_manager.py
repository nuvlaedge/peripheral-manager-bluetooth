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
import requests
#from bluetooth.ble import DiscoveryService
from threading import Event


scanning_interval = 30
KUBERNETES_SERVICE_HOST = os.getenv('KUBERNETES_SERVICE_HOST')
namespace = os.getenv('MY_NAMESPACE', 'nuvlabox')


def init_logger():
    """ Initializes logging """

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def wait_bootstrap(api_url):
    """
    Waits for the NuvlaBox to finish bootstrapping, by checking
        the context file.
    :returns
    """
    while True:
        try:
            logging.info(f'Waiting for {api_url}...')
            r = requests.get(api_url + '/healthcheck')
            r.raise_for_status()
            if r.status_code == 200:
                break
        except:
            time.sleep(15)

    logging.info('NuvlaBox has been initialized.')
    return


def bluetoothCheck(api_url, mac_addr):
    """ Checks if peripheral already exists """
    identifier = mac_addr
    try:
        r = requests.get(f'{api_url}/{identifier}')
        if r.status_code == 404:
            return False
        elif r.status_code == 200:
            return True
        else:
            r.raise_for_status()
    except requests.exceptions.InvalidSchema:
        logging.error(f'The Agent API URL {api_url} seems to be malformed. Cannot continue...')
        raise
    except requests.exceptions.ConnectionError as ex:
        logging.error(f'Cannot reach out to Agent API at {api_url}. Can be a transient issue: {str(ex)}')
        raise
    except requests.exceptions.HTTPError as e:
        logging.warning(f'Could not lookup peripheral {identifier}. Assuming it does not exist')
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


# def bleDeviceDiscovery():
#     service = DiscoveryService("hci0")
#     devices = service.discover(2)
#     return devices


def compareBluetooth(bluetooth, ble):
    output = []

    for device in bluetooth:
        if device[0] not in ble:
            d = {
                "identifier": device[0],
                "class": device[2],
                "interface": "Bluetooth"
            }

            if device[1] != "":
                d["name"] = device[1]

            output.append(d)

    for device_id, device_name in ble.items():
        d = {
            "identifier": device_id,
            "class": "",    # TODO
            "interface": "Bluetooth-LE"
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
    classes = {0: {'major': 'Miscellaneous',
                     'minor': {}},
               1: {
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
               2: {
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
               3: {
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
               4: {
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
               5: {
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
               6: {
                   'major': 'Imaging',
                   'minor': {
                       'bitwise': True,
                       '4': 'Display',
                       '8': 'Camera',
                       '16': 'Scanner',
                       '32': 'Printer'
                   }
               },
               7: {
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
               8: {
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
               9: {
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


def bluetoothManager():

    output = {}

    try:
        # list
        bluetoothDevices = deviceDiscovery()
        logging.info(bluetoothDevices)
    except:
        bluetoothDevices = []
        logging.exception("Failed to discover BT devices")

    bleDevices = {}
    # TODO: implement reliable BLE discovery that works for RPi
    # try:
    #     # dict
    #     bleDevices = bleDeviceDiscovery()
    #     logging.info(bleDevices)
    # except:
    #     bleDevices = {}
    #     logging.exception("Failed to discover BLE devices")

    # get formatted list of bt devices [{},...]
    bluetooth = compareBluetooth(bluetoothDevices, bleDevices)
    if len(bluetooth) > 0:
        for device in bluetooth:
            name = device.get("name", "unknown")
            output[device['identifier']] = {
                    "available": True,
                    "name": name,
                    "classes": cod_converter(device.get("class", "")),
                    "identifier": device.get("identifier"),
                    "interface": device.get("interface", "Bluetooth"),
                }

    return output


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


def post_peripheral(api_url: str, body: dict) -> dict:
    """ Posts a new peripheral into Nuvla, via the Agent API

    :param body: content of the peripheral
    :param api_url: URL of the Agent API for peripherals
    :return: Nuvla resource
    """

    try:
        r = requests.post(api_url, json=body)
        r.raise_for_status()
        return r.json()
    except:
        logging.error(f'Cannot create new peripheral in Nuvla. See agent logs for more details on the problem')
        # this will be caught by the calling block
        raise


def delete_peripheral(api_url: str, identifier: str, resource_id=None) -> dict:
    """ Deletes an existing peripheral from Nuvla, via the Agent API

    :param identifier: peripheral identifier (same as local filename)
    :param api_url: URL of the Agent API for peripherals
    :param resource_id: peripheral resource ID in Nuvla
    :return: Nuvla resource
    """

    if resource_id:
        url = f'{api_url}/{identifier}?id={resource_id}'
    else:
        url = f'{api_url}/{identifier}'

    try:
        r = requests.delete(url)
        r.raise_for_status()
        return r.json()
    except:
        logging.error(f'Cannot delete peripheral {identifier} from Nuvla. See agent logs for more info about the issue')
        # this will be caught by the calling block
        raise


def remove_legacy_peripherals(api_url: str, peripherals_dir: str, protocols: list):
    """ In previous versions of this component, the peripherals were stored in an incompatible manner.
    To avoid duplicates, before starting this component, we make sure all legacy peripherals are deleted

    :param api_url: agent api url for peripherals
    :param peripherals_dir: path to peripherals dir
    :param protocols: list of protocols to look for
    :return:
    """

    for proto in protocols:
        if not proto:
            # just to be sure we don't delete the top directory
            continue

        path = f'{peripherals_dir}{proto}'
        if os.path.isdir(path):
            for legacy_peripheral in os.listdir(path):
                with open(f'{path}/{legacy_peripheral}') as lp:
                    nuvla_id = json.load(lp).get("resource_id")

                # if it has a nuvla_id, there it must be removed from Nuvla
                if nuvla_id:
                    try:
                        delete_peripheral(api_url, f"{proto}/{legacy_peripheral}", resource_id=nuvla_id)
                        continue
                    except:
                        pass

                logging.info(f'Removed legacy peripheral {proto}/{legacy_peripheral}. If it still exists, it shall be re-created.')
                os.remove(f'{path}/{legacy_peripheral}')

            # by now, dir must be empty, so this shall work
            os.rmdir(path)
            logging.info(f'Removed all legacy peripherals for interface {proto}: {path}')


def get_saved_peripherals(api_url, protocol):
    """
    To be used at bootstrap, to check for existing peripherals, just to make sure we delete old and only insert new
    peripherals, that have been modified during the NuvlaBox shutdown

    :param api_url: url of the agent api for peripherals
    :param protocol: protocol name = interface
    :return: map of device identifiers and content
    """

    query = f'{api_url}?parameter=interface&value={protocol}'
    r = requests.get(query)
    r.raise_for_status()

    return r.json()


if __name__ == "__main__":

    init_logger()
    logging.info('BLUETOOTH MANAGER STARTED')
    e = Event()

    peripheral_path = '/srv/nuvlabox/shared/.peripherals/'
    agent_api_endpoint = 'localhost:5080' if not KUBERNETES_SERVICE_HOST else f'agent.{namespace}'
    base_api_url = f"http://{agent_api_endpoint}/api"
    API_URL = f"{base_api_url}/peripheral"

    wait_bootstrap(base_api_url)

    remove_legacy_peripherals(API_URL, peripheral_path, ["bluetooth"])

    old_devices = get_saved_peripherals(API_URL, 'Bluetooth')

    while True:

        current_devices = bluetoothManager()
        logging.info('CURRENT DEVICES: {}'.format(current_devices))
        
        if current_devices != old_devices:

            publishing, removing = diff(old_devices, current_devices)

            for device in publishing:

                peripheral_already_registered = bluetoothCheck(API_URL, device)

                if not peripheral_already_registered:

                    logging.info('PUBLISHING: {}'.format(current_devices[device]))
                    try:
                        resource = post_peripheral(API_URL, current_devices[device])
                    except Exception as ex:
                        logging.error(f'Unable to publish peripheral {device}: {str(ex)}')
                        continue

                old_devices[device] = current_devices[device]

            for device in removing:
                
                logging.info('REMOVING: {}'.format(old_devices[device]))

                peripheral_already_registered = bluetoothCheck(API_URL, device)

                if peripheral_already_registered:
                    try:
                        resource = delete_peripheral(API_URL, device)
                    except:
                        logging.exception(f'Cannot delete {device} from Nuvla')
                        continue
                else:
                    logging.warning(f'Peripheral {device} seems to have been removed already')

                del old_devices[device]

        e.wait(timeout=scanning_interval)
