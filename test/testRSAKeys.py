# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 21:17:37 2016

@author: vsuha
"""

from Crypto.PublicKey import RSA #to install, do 'sudo pip install pycrypto' or 'sudo pip install crypto', i installed so many things I already forgot..oops
from Crypto import Random
from Crypto.Hash import SHA256
from datetime import datetime

device_key = '12345' #from registered-widgets.txt, I guess it doesn't matter how fancy this is since we are encrypting it
timestamp = str(datetime.now()) #we want to encrypt the key & timestamp and pass that to the server

'''
tips for using pycrypto
http://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/
'''

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
#print key

#try to sign the key, this code crashes my IDE...
'''
hash = SHA256.new(device_key).digest()
signature = key.sign(hash, '')
'''


'''
First, we extract the public key from the key pair and use it to encrypt some data. 
32 is a random parameter used by the RSA algorithm to encrypt the data. 
This step simulates us publishing the encryption key and someone using it to encrypt some data before sending it to us.
'''
public_key = key.publickey()
enc_data = public_key.encrypt(device_key + ' ' + timestamp, 32) #just putting spaces to seperate values, we can use something else
#we will pass this enc_data to the server, so in the widget code line 72

#print enc_data


#then to decrypt => we just use the private key to decrypt the data.
magicKey = key.decrypt(enc_data) #THIS will happen on the server side
#print magicKey
