from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes


def aes_encrypt(message_body, message_title):
    # Generate a random 128 bits (16 bytes) long key to be used for encryption/decryption
    key = get_random_bytes(16)

    # Create an AES object
    cipher_aes = AES.new(key, AES.MODE_CTR)

    # Encrypt
    # Will return the encrypted message and the MAC tag (hash value) of the message
    ciphertext_body = cipher_aes.encrypt(message_body.encode('utf-8'))
    ciphertext_title = cipher_aes.encrypt(message_title.encode('utf-8'))

    return key, ciphertext_body, ciphertext_title


def rsa_encrypt(recipient_key, aes_key):
    cipher_rsa = PKCS1_OAEP.new(RSA.importKey(recipient_key))
    return cipher_rsa.encrypt(aes_key)


def rsa_decrypt(private_key, cipher_text):
    decryptor = PKCS1_OAEP.new(private_key)
    plain_text = decryptor.decrypt(cipher_text)
    return plain_text


def encrypt_message(message_body, message_title, recipient_rsa_public_key):
    # Encrypt the message using AES
    aes_key, ciphertext_body, ciphertext_title = aes_encrypt(message_body, message_title)

    # Encrypt the generated AES key using RSA
    encrypted_aes_key = rsa_encrypt(recipient_rsa_public_key, aes_key)

    return encrypted_aes_key, ciphertext_body, ciphertext_title