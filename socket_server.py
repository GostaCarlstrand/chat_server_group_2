import json
import socket
import sys
import threading
import queue
import time

import requests
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA

HOST = "127.0.0.1"
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


def import_key_encrypt_ip(public_key_pem):
    public_key = RSA.importKey(public_key_pem)
    rsa_cipher = PKCS1_OAEP.new(public_key)
    cipher_text = rsa_cipher.encrypt(b'127.0.0.1')
    return cipher_text


def client_handler(client_socket, broadcast_queue, client_list):
    print("Started client handler thread")
    while True:
        try:
            # Get data from client, BLOCKING
            message = client_socket.recv(1024)
            message = message.decode('utf-8')
            print("Got message", message)

            # Create a dictionary that contains the socket
            # used to receive the message, and the message
            message_dict = {
                'sender_socket': client_socket,
                'message': message.encode('utf-8')
            }
            # Add the dictionary to the broadcast queue
            broadcast_queue.put(message_dict)
        except ConnectionResetError:
            print("A client left the chat")
            client_list.remove(client_socket)
            break


def broadcast(client_list, broadcast_queue):
    print("Broadcast thread started")
    while True:
        # Wait for a message to broadcast
        message_dict = broadcast_queue.get()
        print("Broadcast thread got a message to send")
        for client in client_list:
            if client != message_dict['sender_socket']:
                client.send(message_dict['message'])


def get_api_data(url):
    data = requests.get(url)
    if data.status_code != 200:
        print(f"Request to url {url} failed.")
        sys.exit()
    return json.loads(data.text)


def main():
    # public_key_pem, private_key_pem = generate_keys()
    chat_id = input('What is the chat id you wish to connect to? Response must be in the form of an integer.\n')
    public_key_pem_response = requests.get(f'http://127.0.0.1:5010/api/v1.0/{chat_id}')

    def is_pub_key_none(response):
        if response:
            return response
        else:
            time.sleep(5)
            print(1)
            response = requests.get(f'http://127.0.0.1:5010/api/v1.0/{chat_id}')
            return is_pub_key_none(response.content)

    public_key_pem = is_pub_key_none(public_key_pem_response.content)
    encrypted_ip = import_key_encrypt_ip(public_key_pem)
    r = requests.post(f'http://127.0.0.1:5010/api/v1.0/{chat_id}/ip', data=encrypted_ip)
    print(r.content.decode('utf-8'))
    # Create a socket that uses ip4 (AF_INET), and TCP (SOCK_STREAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))

    server_socket.listen()
    # Create a list of all connected clients
    client_list = []

    # Create a queue for communication between the client threads and the broadcast thread
    broadcast_queue = queue.Queue()

    # Start the broadcast thread. The client_list is mutable, so the thread and the main thread
    # will use the same list, not a copy
    broadcast_thread = threading.Thread(target=broadcast, args=(client_list, broadcast_queue))
    broadcast_thread.start()
    while True:
        # Wait for connection, BLOCKING
        client_socket, client_address = server_socket.accept()
        print(f'Client connect from {client_address}')
        # Start thread for client
        client_thread = threading.Thread(target=client_handler, args=(client_socket, broadcast_queue, client_list))
        # Add the new client_socket to the list of clients
        client_list.append(client_socket)
        client_thread.start()


if __name__ == '__main__':
    main()
