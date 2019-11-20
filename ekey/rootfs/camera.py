import os
import requests
import json
import time

from flask import Flask
app = Flask(__name__)

ha_api_url = os.getenv('HA_API_URL', 'http://192.168.1.143:8123/api')
ha_access_token = os.getenv('HA_ACCESS_TOKEN', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI0YzVhMjU3ZDg0ZmQ0YTJmOWVkNDk3YjNiZTVlZmE1OSIsImlhdCI6MTU3NDIzNzg4NCwiZXhwIjoxODg5NTk3ODg0fQ.l19QnvcKsyhg1g31_e-HUb_UOnrM4eIteDiu28PMAhU')
ha_opritmotion_entity = os.getenv('HA_OPRITMOTION_ENTITY', 'binary_sensor.opritmotion')
ha_keulsewegmotion_entity = os.getenv('HA_KEULSEWEGMOTION_ENTITY', 'binary_sensor.keulsewegmotion')
ha_tuinmotion_entity = os.getenv('HA_TUINMOTION_ENTITY', 'binary_sensor.tuinmotion')


@app.route("/")
def default():
    return "OK"


@app.route("/oprit")
def opritmotion():
    return trigger_ha_entity(ha_opritmotion_entity)


@app.route("/keulseweg")
def keulsewegmotion():
    return trigger_ha_entity(ha_keulsewegmotion_entity)


@app.route("/tuin")
def tuinmotion():
    return trigger_ha_entity(ha_tuinmotion_entity)


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
            self.headers.update({'Authorization': 'Bearer {0}'.format(access_token)})

    def get_entity(self, name):
        url = '{}/states/{}'.format(self.base_url, name)
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise HomeAssistantApiException(
                response.status_code, 'Error getting entity from Home Assistant with: {0}'.format(response.content))

        return response.json()

    def update_entity(self, name, data):
        url = '{}/states/{}'.format(self.base_url, name)
        response = requests.post(url, headers=self.headers, data=json.dumps(data))

        if response.status_code != 200:
            raise HomeAssistantApiException(
                response.status_code, 'Error updating entity at Home Assistant with: {0}'.format(response.content))

        return response.json()


class HomeAssistantApiException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999)
