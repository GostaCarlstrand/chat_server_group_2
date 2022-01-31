import os


import paho.mqtt.client as paho
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey.RSA import RsaKey
from Cryptodome.Random import get_random_bytes

from flask_login import current_user
from controllers.user_controller import get_user_by_id


def create_message(title, body, receiver_id):
    from models import Message, User
    user = current_user
    message = Message(title=title, body=body, sender_id=user.id)
    recipient = User.query.filter_by(id=receiver_id).first()
    if not recipient.signed_in:
        from controllers.mqtt_controller import connect_mqtt
        mqtt_publisher = connect_mqtt(current_user.id)
        mqtt_publisher.loop_start()
        mqtt_publisher.publish(f'{receiver_id}', f"You've received a message from {user.name}")
        mqtt_publisher.loop_stop()

    receiver_id = int(receiver_id)
    receiver = get_user_by_id(receiver_id)
    message.receivers.append(receiver)
    from app import db
    db.session.add(message)
    db.session.commit()


def get_user_messages():
    return current_user.recv_messages


def get_all_messages():
    from models import Message
    message = Message.query.all()
    return message


# def aes_encrypt(message):
#     from models import Message
#     # Generate a random 512 bits long key
#     key = get_random_bytes(64)
#     # Create an AES object
#     cipher_aes = AES.new(key, AES.MODE_AEX)
#
#     # Encrypt
#     # Will return the encrypted message and the MAC tag (hash value) of the message
#     ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode('utf-8'))
#
#     return key, ciphertext, cipher_aes.nonce, tag
#

# def aes_decrypt(aes_key, cipher_text, nonce, tag):
#     # Create an AES object
#     cipher_aes = AES.new(aes_key, AES.MODE_AEX, nonce)
#     decrypted_data = cipher_aes.decrypt_and_verify(cipher_text, tag)
#
#
# def generate_rsa_key(key_name, key_size=2048):
#     key = RSA.generate(key_size)
#     private_key = key.export_key()
#     with open(f'./rsa_keys/{key_name}_private.pem', 'wb') as out_file:
#         out_file.write(private_key)
#
#     public_key = key.public_key().export_key()
#     with open(f'./rsa_keys/{key_name}_public.pem', 'wb') as out_file:
#         out_file.write(public_key)
#
#
# def rsa_encrypt(rsa_key_name, message):
#     if type(rsa_key_name) != RsaKey:
#         if os.path.isfile(f'./rsa_keys/{rsa_key_name}.pem'):
#             recipient_key = RSA.importKey(open(f'./rsa_keys/{rsa_key_name}.pem', 'rb').read())
#         else:
#             print(f'No key file named {rsa_key_name}.pem found')
#             return ""
#     rsa_cipher = PKCS1_OAEP.new(recipient_key)
#     return rsa_cipher.encrypt(message)
#
#
# def rsa_decrypt(cipher_text, rsa_key_name):
#     if type(rsa_key_name) != RsaKey:
#         if os.path.isfile(f'./rsa_keys/{rsa_key_name}.pem'):
#             rsa_key_name = RSA.importKey(open(f'./rsa_keys/{rsa_key_name}.pem', 'rb').read())
#         else:
#             print(f'No key file named {rsa_key_name}.pem found')
#             return ""
#     cipher_rsa = PKCS1_OAEP.new(rsa_key_name)
#     return cipher_rsa.decrypt(cipher_text)
#
#
# def encrypt_message(message, recipient_rsa_key_name):
#     # Encrypt the message using AES
#     aes_key, aes_cipher, aes_nonce, aes_tag = aes_encrypt(message)
#
#     # Encrypt the generated AES key using RSA
#     encrypted_aes_key = rsa_encrypt(recipient_rsa_key_name, aes_key)
#
#     return (encrypted_aes_key, aes_nonce, aes_tag, aes_cipher)
#
#
# def decrypt_message(private_rsa_key_name, encrypted_data):
#     # Decrypt the AES key using RSA
#     encrypted_aes_key, aes_nonce, aes_tag, aes_cipher = encrypted_data
#     # Decrypt the generated AES key using RSA
#     aes_key = rsa_decrypt(encrypted_aes_key, private_rsa_key_name)
#     # Decrypt the message using AES
#     return aes_decrypt(aes_key, aes_cipher, aes_nonce, aes_tag)
#
#
# def read_encrypted_data():
#     priv_rsa_key = RSA.importKey(open(f''))
#
#
# def store_encrypted_data(filename, encrypted_data):
#     with open(f'.encrypted_data/{filename}.bin', 'wb') as out_file:
#         for data in encrypted_data
#
#
# def temp_call_crypto_functions():
#     encrypted_data = encrypt_message('This is my super secret message', recipient_key_name)
#
#     plaintext = decrypt_message(private_rsa_key_name, encrypted_data)