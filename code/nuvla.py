import requests
import os
import sys
import json

def login_push(session_template, url, cookie_file):
    return requests.post(url, headers={'content-type':'application/json', 'accept':'application/json'}, cookies=cookie_file, data=session_template)

def login(activated_path, nuvla_endpoint, cookies_file, extra_flags):

    activated = json.load(open(activated_path))
    api_key = activated['api-key']
    secret_key = activated['secret-key']

    # Then we have to login first
    session_template = {
        "template": {
            "href": "session-template/api-key",
            "key": api_key,
            "secret": secret_key
        }
    }

    url = '{}/api/session'.format(nuvla_endpoint)

    if cookies_file:
        session_alive = requests.get(url, headers={'content-type':'application/json'}, cookies=cookies_file)

        if session_alive:
            login_push(session_template, url, cookies_file)
    else:
        login_push(session_template, url, cookies_file)

def add_bluetooth_peripheral(put_json, nuvla_endpoint, nuvla_id, activated_path, cookies_file, extra_flags):
   
    login(activated_path, nuvla_endpoint, cookies_file, extra_flags)

    url = '{}/api/{}'.format(nuvla_endpoint, nuvla_id) 
    r = requests.put(url, cookies=cookies_file, headers={'content-type':'application/json', 'accept': 'application/json'}, data=put_json)

def remove_bluetooth_peripheral(resource_id, nuvla_endpoint, data, activated_path, cookies_file, extra_flags):
    
    login(activated_path, nuvla_endpoint, cookies_file, extra_flags)

    url = '{}/api/{}'.format(nuvla_endpoint, resource_id) 
    r = requests.delete(url, headers={'content-type':'application/json'}, cookies=cookies_file)
