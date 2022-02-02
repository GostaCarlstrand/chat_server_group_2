from random import random
import paho.mqtt.client as paho
import requests as requests
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Random import get_random_bytes
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey.RSA import RsaKey


CLIENT_ID = f'{1}'
BROKER = '104.248.47.103'
PORT = 1883
USERNAME = 'kyh_1'
PASSWORD = 'kyh1super2'


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker')
    else:
        print(f'Failed to connect to Broker. Error code {rc}')


def connect_mqtt():
    # Create a MQTT client object.
    # Every client has an id
    client = paho.Client(CLIENT_ID)
    # Set username and password to connect to broker
    client.username_pw_set(USERNAME, PASSWORD)

    # When connection response is received from broker
    # call the function on_connect
    client.on_connect = on_connect

    # Connect to broker
    client.connect(BROKER, PORT)

    return client


def on_subscribe(client, userdata, mid, granted_qos):
    print(f'Subscribed')


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f'{msg.topic}: {payload}')


def subscribe(client, user_id):
    # Subscribe on topic user_id
    client.subscribe(f'{user_id}')
    client.on_message = on_message


def generate_rsa_keys(key_name, key_size=3072):
    # Generate a key-pair with the specified key size
    key = RSA.generate(key_size)

    # Extract the private key
    private_key = key.export_key()
    with open(f'./rsa_keys/{key_name}_private.pem', 'wb') as out_file:
        out_file.write(private_key)

    # Extract the public key
    public_key = key.public_key().export_key()
    with open(f'./rsa_keys/{key_name}_public.pem', 'wb') as out_file:
        out_file.write(public_key)


def main():
    user_id = input('To create a key pair to use for encryption and decryption of your messages enter your user id.')
    generate_rsa_keys(name)
    r = requests.post(f'http://127.0.0.1:5010/api/v1.0/{user_id}', data=f'./rsa_keys/{user_id}_public.pem')

    topic = input('Which user id would you like to subscribe to?')
    client = connect_mqtt()
    # When we have subscribed to a topic, call this function
    client.on_subscribe = on_subscribe

    subscribe(client, topic)
    client.loop_forever()


if __name__ == '__main__':
    main()