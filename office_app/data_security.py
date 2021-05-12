"""
Created By: Jacob Lattergrass
Date: 2020/03/17
Packages Used: Cryptography and Django

This file is being used to generate and store keys.
It also contains the functions that will be used in
data-encryption and decryption.

List of Functions Below:
    generate_keys()
    sotre_private_key()
    store_public_key()
    get_hr_private_key()
    get_public_key()
    encrypt_hr_file()
    check_key_access()
"""
from django.core.exceptions import ObjectDoesNotExist
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
import base64
from .models import KeyAccess

'''
    Save private key
    Written By: Jacob Lattergrass
    :param private_key: the private key you want to store
    :param dept: the department that will have this key
    :param key_name: the name you wish to assign to the key in the system
'''


def store_private_key(private_key, dept, key_name):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open('security/private_keys/' + dept + '/' + key_name + '.pem', 'wb') as f:
        f.write(pem)


'''
    Save public key
    Written By: Jacob Lattergrass
    :param public_key: the private key you want to store
    :param key_name: the name you wish to assign to the key in the system
'''


def store_public_key(public_key, key_name):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with open('security/public_keys/' + key_name + '.pem', 'wb') as f:
        f.write(pem)


'''
    Generate keys
    Written By: Jacob Lattergrass
    :param dept: the department that will have this key
    :param key_name: the name you wish to assign to the key in the system
'''


def generate_keys(dept, key_name):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    if __name__ == '__main__':
        public_key = private_key.public_key()

        store_private_key(private_key, dept, key_name)
        store_public_key(public_key, key_name)


'''
    Retrieve private key from hr folder
    Written By: Jacob Lattergrass
    :returns private_key: the private key for this department
'''


def get_hr_private_key(key_name):
    try:
        with open('security/private_keys/hr/' + key_name + '.pem', 'rb') as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
            return private_key
    except ObjectDoesNotExist:
        print('Error: Key file does not exist')


'''
    Retrieve public key
    Written By: Jacob Lattergrass
    :param key_name: name of the public key you want to use
    :returns private_key: the private key for this department
'''


def get_public_key(key_name):
    try:
        with open('security/public_keys/' + key_name + '.pem', 'rb') as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
            return public_key
    except ObjectDoesNotExist:
        print('Error: Key file does not exist')


'''
    Encrypt a file for hr
    Written By: Jacob Lattergrass
    :param key_name: name of the public key to be used for encrypting
    :param file: file to be encrypted
    :returns encrypted_data: the encrypted file
'''


def encrypt_hr_file(key_name, file):
    public_key = get_public_key(key_name)
    encrypted_data = public_key.encrypt(
        base64.b64encode(file),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_data


'''
    Decrypt a file for hr
    Written By: Jacob Lattergrass
    :param key_name: name of the private key used for decrypting
    :param encrypted_file: file to be decrypted
    :returns original_file: the decrypted file
'''


def decrypt_hr_file(key_name, encrypted_file):
    private_key = get_hr_private_key(key_name)
    original_file = private_key.decrypt(
        encrypted_file,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256
        )
    )
    # TODO: As it stands now, we need a way to load the encrypted file from the server.
    # Try using the with open() method, though at this stage the issue is finding the right PDF
    return original_file


# TODO: We still need more information on how we plan to use these functions.
'''
    Check employee authority
    Written By: Jacob Lattergrass
    :param employee_id: id of the employee trying to use the key
    :param key_name: name of the key used being used
    :returns True or False
'''


def check_key_access(employee_id, key_name):
    employee = KeyAccess.objects.filter(employeeID=employee_id)
    for entry in employee:
        if entry.keyName == key_name:
            return True
    return False
