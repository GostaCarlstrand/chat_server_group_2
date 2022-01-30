import json
import socket
import sys
import threading
import time

import requests
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import binascii

PORT = 9876


def generate_keys():
    key_pair = RSA.generate(3072)
    public_key = key_pair.public_key()
    # public_key.export_key('PEM')
    return public_key.export_key('PEM'), key_pair.export_key('PEM', '1234')


def decrypt_ip(key_pair, cipher_text):
    key = RSA.importKey(key_pair, '1234')
    decryptor = PKCS1_OAEP.new(key)
    host = decryptor.decrypt(cipher_text)
    return host


def get_api_data(url):
    data = requests.get(url)
    if data.status_code != 200:
        print(f"Request to url {url} failed.")
        sys.exit()
    return json.loads(data.text)


def input_handler(client_socket):
    while True:
        try:
            # Get user message - BLOCKING
            message = input()
            # Send the message
            client_socket.send(message.encode('utf-8'))
        except UnicodeDecodeError:
            print("Unicode error")
        break


def main():
    chat_id = input('What is the chat id you wish to connect to? Response must be in the form of an integer.\n')
    public_key_pem, private_key_pem = generate_keys()
    r = requests.post(f'http://127.0.0.1:5010/api/v1.0/{chat_id}', data=public_key_pem)
    print(r.content.decode('utf-8'))
    encrypted_ip_response = requests.get(f'http://127.0.0.1:5010/api/v1.0/{chat_id}/ip')

    def is_encrypted_ip_none(response):
        if response:
            return response
        else:
            time.sleep(1)
            print(1)
            response = requests.get(f'http://127.0.0.1:5010/api/v1.0/{chat_id}/ip')
            return is_encrypted_ip_none(response.content)

    encrypted_ip = is_encrypted_ip_none(encrypted_ip_response.content)
    host = decrypt_ip(private_key_pem, encrypted_ip)
    # host = json.loads(encrypted_ip)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, PORT))

    input_thread = threading.Thread(target=input_handler, args=(client_socket, ))
    input_thread.start()
    while True:
        # Receive message from server - BLOCKING
        message = client_socket.recv(1024)
        message = message.decode('utf-8')
        print(message)


if __name__ == '__main__':
    main()