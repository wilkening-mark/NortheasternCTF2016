#!/usr/bin/env python
import json
import socket
import smbus
import subprocess
import time
import threading
from uuid import getnode as get_mac
import ssl

#Classes
from AVRChip import AVRChip
from Logger import Logger
from ServerConnection import ServerConnection

# This is a (bad) example of the "something you have" portion of the authentication.
DEVICE_KEY = '12345' #Default


def main():
    """
    Main program loop. Sets up the connections to the AVR and the server, then
    reads key presses and sends them to the server.
    """
    avr = AVRChip()
    avr.reset_keys() # clear the key buffer on the AVR
    avr.led_off()
    logger = Logger()

    try:
        with open('/etc/device_key.txt', 'r') as f:
            for line in f:
                line = line.strip()
                DEVICE_KEY = line
    except IOError:
        DEVICE_KEY = '12345'

    try:
        server = ServerConnection(logger, DEVICE_KEY)
        
        server.connect()

        buf = ""

        while (True):
            c = avr.read_key()

            # read_key() will always return a character. NULL means no new
            # key presses.
            if c == '\0':
                time.sleep(0.1)
                continue

            buf += c

            logger.info('KEY PRESSED - ' + str(c) + '\n')

            # maximum size to avoid running out of memory
            if len(buf) > 16:
                logger.error('Reached maximum buffer size')
                buf = ""

            if c == '#':
                # These are the cases where we should continue reading input.
                # Otherwise, the # character always terminates the input.
                if buf in ('*#', '*#*#', '*#*#*#'):
                    continue

                if buf == '*#*#*#*#':
                    if server.register_device():
                        logger.info('Registration successful')
                        avr.avr_indicate_success()
                    else:
                        logger.info('Registration unsuccessful')
                        avr.avr_indicate_failure()
                elif len(buf) == 7:
                    password = buf[:6]

                    if server.open_door(password):
                        logger.info('Door open successful')
                        avr.avr_indicate_success()
                    else:
                        logger.info('Door open unsuccessful')
                        avr.avr_indicate_failure()
                elif len(buf) == 14:
                    if buf[6] != '*':
                        logger.error('Invalid entry')
                        buf = ""
                        continue

                    current_password = buf[:6]
                    new_password = buf[7:-1]

                    if server.change_password(current_password, new_password):
                        logger.info('Password change successful')
                        avr.avr_indicate_success()
                    else:
                        logger.info('Password change unsuccessful')
                        avr.avr_indicate_failure()
                elif len(buf) == 16:
                    if buf[8] != '*':
                        logger.error('Invalid entry')
                        buf = ""
                        continue

                    master_password = buf[:8]
                    new_password = buf[9:-1]

                    if server.change_password_master(master_password, new_password):
                        logger.info('Password change successful')
                        avr.avr_indicate_success()
                    else:
                        logger.info('Password change unsuccessful')
                        avr.avr_indicate_failure()
                else:
                    logger.error('Invalid entry')

                buf = ""
    except KeyboardInterrupt:
        pass
    finally:
        logger.close()

if __name__ == '__main__':
    main()
