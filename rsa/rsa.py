from Cryptodome.PublicKey import RSA

from controllers.user_controller import get_user_by_id
from models import User


def generate_rsa_pair(user):

    key = RSA.generate(2048)

    # Both keys in PEM
    private_key = key.export_key()
    public_key = key.public_key().export_key()

    with open(f'./rsa_private_key/{user}_private.pem', 'wb') as out_file:
        out_file.write(private_key)

    # Returns so that it is saved in the user database
    return public_key
