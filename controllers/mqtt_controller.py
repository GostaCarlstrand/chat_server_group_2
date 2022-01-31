import os
import paho.mqtt.client as paho

BROKER = os.environ.get('MQTT_BROKER_URL')
PORT = int(os.environ.get('MQTT_BROKER_PORT'))
USERNAME = os.environ.get('MQTT_USERNAME')
PASSWORD = os.environ.get('MQTT_PASSWORD')


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f'{client} Connected to MQTT Broker')
    else:
        print(f'Failed to connect to Broker. Error code {rc}')


def connect_mqtt(client_id):
    # Create a MQTT client object.
    # Every client has an id
    client = paho.Client(f'Client_id_{client_id}')
    # Set username and password to connect to broker
    client.username_pw_set(USERNAME, PASSWORD)

    # When connection response is received from broker
    # call the function on_connect
    client.on_connect = on_connect

    # Connect to broker
    client.connect(BROKER, PORT)

    return client