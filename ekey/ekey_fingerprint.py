import os
import socket
import requests
import json
import time
from flask import Flask
app = Flask(__name__)
ha_api_url = os.getenv('HA_API_URL', 'http://localhost:8123/api')
ha_access_token = os.getenv(
    'HA_ACCESS_TOKEN', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI0YjI5MjgxMzI0ZGI0MWY5ODc1MTQzMDhmMTNkMjU3YSIsImlhdCI6MTU0NzgxODEzMywiZXhwIjoxODYzMTc4MTMzfQ.e4S_DpiD5-zMGKOOlXsqbQw_VMt4t6FRwLqggPIUunE')
ha_ekeygarage_entity = os.getenv(
    'HA_EKEY_GARAGE_ENTITY', 'binary_sensor.ekey_garage')
ha_ekeybijkeuken_entity = os.getenv(
    'HA_EKEY_BIJKEUKEN_ENTITY', 'binary_sensor.ekey_bijkeuken')
ha_ekeykeuken_entity = os.getenv(
    'HA_EKEY_KEUKEN_ENTITY', 'binary_sensor.ekey_keuken')
ha_ekeyvoordeur_entity = os.getenv(
    'HA_EKEY_VOORDEUR_ENTITY', 'binary_sensor.ekey_voordeur')

UDP_PORT = 56000


class udpserver:
    def __init__(self, UDP_IP, UDP_PORT, msg_len=1024):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.msg_len = msg_len

    def __iter__(self):
        return self

    def __next__(self):
        try:
            data, addr = self.sock.recvfrom(self.msg_len)
            return data, addr
        except Exception as e:
            print("Got exception trying to recv %s" % e)
            raise StopIteration

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.sock.close()


def trigger_ha_entity(name):
    client = HomeAssistantApiClient(ha_api_url, ha_access_token)

    try:
        entity = client.get_entity(name)
    except HomeAssistantApiException as e:
        return e.message, e.status_code

    entity = {'state': 'on', 'attributes': entity['attributes']}
    try:
        client.update_entity(name, entity)
    except HomeAssistantApiException as e:
        return e.message, e.status_code

    time.sleep(1)

    entity = {'state': 'off', 'attributes': entity['attributes']}
    try:
        client.update_entity(name, entity)
    except HomeAssistantApiException as e:
        return e.message, e.status_code

    return "OK"


class HomeAssistantApiClient(object):
    def __init__(self, base_url, access_token=None):
        self.base_url = base_url
        self.headers = {'content-type': 'application/json'}
        if access_token is not None:
            self.headers.update(
                {'Authorization': 'Bearer {0}'.format(access_token)})

    def get_entity(self, name):
        url = '{}/states/{}'.format(self.base_url, name)
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise HomeAssistantApiException(
                response.status_code, 'Error getting entity from Home Assistant with: {0}'.format(response.content))

        return response.json()

    def update_entity(self, name, data):
        url = '{}/states/{}'.format(self.base_url, name)
        response = requests.post(
            url, headers=self.headers, data=json.dumps(data))

        if response.status_code != 200:
            raise HomeAssistantApiException(
                response.status_code, 'Error updating entity at Home Assistant with: {0}'.format(response.content))

        return response.json()


class HomeAssistantApiException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


startserver = udpserver(UDP_IP, UDP_PORT)
for (data, addr) in startserver:
    print(data)
    print(addr)
    datasplit = data.decode().split("_")
    # fingerprints
    if datasplit[3] == "80198540170614" and datasplit[4] == "000001":
        trigger_ha_entity(ha_ekeygarage_entity)
    elif datasplit[3] == "80198540170789" and datasplit[4] == "000001":
        trigger_ha_entity(ha_ekeygarage_entity)
    elif datasplit[3] == "80244042170120" and datasplit[4] == "000001":
        trigger_ha_entity(ha_ekeybijkeuken_entity)
    elif datasplit[3] == "80198540170610" and datasplit[4] == "000001":
        trigger_ha_entity(ha_ekeykeuken_entity)
    elif datasplit[3] == "80198540170623" and datasplit[4] == "000001":
        trigger_ha_entity(ha_ekeyvoordeur_entity)
