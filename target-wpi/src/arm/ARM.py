# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 22:34:46 2016

"""

#!/usr/bin/env python
import json
import socket
import smbus
import os
import hashlib
import httplib
import time
import threading
from M2Crypto import m2
from M2Crypto import RSA

class AVRChip(object):
    """
    Class for communicating with the AVR on the CryptoCape.
    """
    AVR_ADDR = 0x42

    def __init__(self):
        self.bus = smbus.SMBus(1) # /dev/i2c-1
    
    def led_on(self):
        self.bus.write_byte(AVRChip.AVR_ADDR, 0x02)

    def led_off(self):
        self.bus.write_byte(AVRChip.AVR_ADDR, 0x03)
    
    def get_status(self):
        #self.bus.write_byte(self.AVR_ADDR, 0x01)
        status_list = self.getByte()
        return status_list      
        
    def send_data(self, data):
        return self.bus.write_i2c_block_data(self.AVR_ADDR, data[0], data[1:])
        
    def resetStatus(self):
        return self.bus.write_i2c_block_data(self.AVR_ADDR, 12, [1,1,1])

    def getByte(self):
        bite = self.bus.read_byte(self.AVR_ADDR)
        return bite
         
    def sendSecret(self,secret):
        print 'sending secret'
        
        pack1 = [0x02, 0x00, 0x00] +  secret[:16]
        pack2 = [0x02, 0x01, 0x10] +  secret[16:]
        print(pack1) 
        print(pack2) 
        self.send_data(pack1)
        self.send_data(pack2)
        return True
        
    def sendUnlockChal(self, challenge):
        print 'sending unlock challenge'
        
        pack1 = [0x03, 0x00, 0x00] + challenge[:16]
        pack2 = [0x03, 0x01, 0x10] +  challenge[16:]
        
        self.send_data(pack1)
        self.send_data(pack2)
        return True
        
    def sendPinChal(self, challenge):
        print 'sending pin challenge'
        
        pack1 = [0x04, 0x00, 0x00] + challenge[:16]
        pack2 = [0x04, 0x01, 0x10] + challenge[16:]
        
        self.send_data(pack1)
        self.send_data(pack2)
        return True
        
class ARM(object):    
    
    def __init__(self, avr):
        self.avr = avr
        try:
            f = open('fingerprint')
            self.fpr = f.read()
            f.close()
        except:
            print("device is not registered")
        
    def registration(self):
        print 'registration reached'
        self.fpr = os.urandom(32).encode('hex')
        payload = json.dumps({'fingerprint': self.fpr}) 
        headers = {"Content-type": "application/json"}
        c = httplib.HTTPConnection('192.168.7.1:5000')
        c.request("POST", "/registration_1", payload, headers) #ARM sends public key to server
        r = c.getresponse()   # Server receives public key
        if r.status == 200:   #Verification from Server
            f = open('fingerprint', 'w')
            f.write(self.fpr)
            f.close()
            d = r.read()
            data = json.loads(d)  #ARM receives the public key 
            sPubkey = data['DHPub']
            prime = data['DHPrime']
            sPubkey = int(sPubkey, 16)
            prime = int(prime, 16) 
            pk = self.genPrivateKey(256)  #32 byte private 
            generator = 2
            dhpub = pow(generator, pk, prime)   
            
            dhpubh = hex(dhpub)[2:-1]
            ss = pow(sPubkey, pk, prime)
            ss = [ord(x) for x in list(hashlib.sha256(hex(ss)[2:-1]).digest())]
            self.avr.sendSecret(ss)
        else:
            return False
        payload = json.dumps({'fingerprint': self.fpr, 'DHPub': dhpubh}) 
        c = httplib.HTTPConnection('192.168.7.1:5000')
        c.request("POST", "/registration_2", payload, headers) #ARM sends server DHPub Value
        r = c.getresponse()
        if r.status == 200:
            print('registration complete')
            return True                   #Registration Complete
        else:
            print('registration failed')
            return False  
              
    def unlock(self):
        fpr = self.fpr
        challenge = json.dumps({'fingerprint': fpr})
        headers = {"Content-type": "application/json"}
        c = httplib.HTTPConnection('192.168.7.1:5000')
        c.request("POST", "/start_unlock", challenge, headers)
        r = c.getresponse()
        if r.status == 200:  # Making sure communication with the server is performed correctly
            d = r.read()
            data = json.loads(d)
            challenge = data['challenge']
            from binascii import unhexlify as unhex
            challenge = [ord(x) for x in list(unhex(challenge))]
            self.avr.sendUnlockChal(challenge)
            # AVR creates HMAC(key, challenge + pin) and sends it to ARM
            
            hmac = []
            while self.avr.get_status() != 0xA4:
                pass
            for i in range(32):
                hmac.append(self.avr.getByte())
            
            hmac = "".join([ hex(x)[2:] if len(hex(x)) == 4 else "0"+hex(x)[2] for x in hmac])
            
            #  POST /unlock
            unlocking = json.dumps({'hash': hmac, 'fingerprint': fpr}) 
            c = httplib.HTTPConnection('192.168.7.1:5000')
            c.request("POST", "/unlock", unlocking, headers)
            r = c.getresponse()  
            if r.status == 200:        #Server validates the request
                d = r.read()
                data = json.loads(d)
                flag = data['flag']
                return flag            #Unlock Complete
            else:
                return False  
        else:
            return False 

    def changePIN(self):
        ##fpr is a global variable
        fpr = self.fpr
        challenge = json.dumps({'fingerprint': fpr})
    
        headers = {"Content-type": "application/json"}
        c = httplib.HTTPConnection('192.168.7.1:5000')
        c.request("POST", "/start_pin_change", challenge, headers)
        r = c.getresponse()
    
        if r.status == 200: 
            d = r.read()
            data = json.loads(d)
            from binascii import unhexlify as unhex
            challenge = data['challenge']
            challenge = [ord(x) for x in list(unhex(challenge))]
            self.avr.sendPinChal(challenge)
            # AVR creates HMAC(key, challenge + pin) and sends it to ARM
            
            from time import sleep
            sleep(0.5) 
            hmac = []
            while self.avr.get_status() != 0xA7:
                # read in hmac    
                pass
            for i in range(64):
		        hmac.append(self.avr.get_status())
            #hmac.append(self.avr.getByte())
            
            hmac = "".join([ hex(x)[2:] if len(hex(x)) == 4 else "0"+hex(x)[2] for x in hmac])
            data = json.dumps({'hash': hmac})
            headers = {"Content-type": "application/json"}
            c = httplib.HTTPConnection('192.168.7.1:5000')
            pin_change = json.dumps({'hash': hmac, 'fingerprint': fpr})
            c.request("POST", '/pin_change', pin_change, headers)

            r = c.getresponse() 
            if r.status == 200:                #Server verifies the signature
                return True                 #changePIN Complete
            else:
                return False                 
        else:
            return False             

    def genRandom(self, bits):
		"""
		Generate a random number with the specified number of bits
		"""
		_rand = 0
		_bytes = bits // 8

		while(_rand.bit_length() < bits):
			# Python 2
			_rand = int(os.urandom(_bytes).encode('hex'), 16)

		return _rand

    def genPrivateKey(self, bits):
		"""
		Generate a private key using a secure random number generator.
		"""
		return self.genRandom(bits)
                   

class Logger(object):
    """
    Logs information to connections on port 6000. Simple way of accessing logs
    using netcat:
                    nc 192.168.7.2 6000
    """
    LOGGER_PORT = 6000

    def __init__(self):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conns = []
        self.thread = threading.Thread(target = self.accept_thread)
        self.thread.start()

    def accept_thread(self):
        """
        Simple thread that waits for connections and appends them to the list
        as they come in.
        """
        self.listen_socket.bind(('', Logger.LOGGER_PORT))
        self.listen_socket.listen(1)
        
        while True:
            try:
                conn, _ = self.listen_socket.accept()
                self.conns.append(conn)
            except:
                break

    def close(self):
        # forces accept() in accept_thread to raise an exception
        self.listen_socket.shutdown(socket.SHUT_RDWR)
        self.listen_socket.close()
        self.thread.join()

    def message(self, msg):
        bad_conns = []

        for conn in self.conns:
            try:
                conn.sendall(msg + "\n")
            except socket.error:
                bad_conns.append(conn)

        for bad_conn in bad_conns:
            self.conns.remove(bad_conn)

    def info(self, msg):
        self.message("INFO: " + msg)

    def error(self, msg):
        self.message("Error: " + msg)

def avr_indicate_success(avr):
    """
    Indicate a successful operation by turning on the LED for 3 seconds.
    """
    os.system('sh correct.sh')

def avr_indicate_failure(avr):
    """
    Indicate a failure by blinking the LED quickly 3 times.
    """
    os.system('sh incorrect.sh')

def main():
    """
    Main program loop. Sets up the connections to the AVR and the server, then
    reads key presses and sends them to the server.
    """
    avr = AVRChip()
    arm = ARM(avr)
    #avr.led_off()
    logger = Logger()       


    while (True):
        c = avr.get_status()
        if c == 0xA1:
            print c
            if arm.registration():
                logger.info('Registration successful') 
                avr_indicate_success(avr)
            else:
                logger.info('Registration unsuccesful')
                avr_indicate_failure(avr)
                avr.resetStatus()
                
        if c == 0xA2:
            print c
            flag = arm.unlock()
            if flag:
                print 'unlock succcess'
                logger.info('Unlock successful %s' % flag)
                avr_indicate_success(avr)
            else:
                print 'unlock failure'
                logger.info('Unlock unsuccessful')
                avr_indicate_failure(avr)
                avr.resetStatus()
                
        if c == 0xA5:
            print c
            if arm.changePIN():
                print 'change pin succesful'
                logger.info('Pin change succesful')
                avr_indicate_success(avr)
            else:
                logger.info('Unlock/Changepin failure')
                avr_indicate_failure(avr)
                avr.resetStatus()
        

           
#    except KeyboardInterrupt:
#        pass
#    finally:
#        logger.close()

if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            pass
