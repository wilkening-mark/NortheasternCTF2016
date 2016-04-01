from uuid import getnode as get_mac
import ssl
import json
import socket
import time


class ServerConnection(object):
    """
    This class manages the connection to the door server. It automatically
    attempts to reconnect to the server every 10 seconds if the connection
    fails.
    """

    # Connect to 192.168.7.1:5000
    SERVER_ADDR = '192.168.7.1'
    SERVER_PORT = 5000

    def __init__(self, logger, device_key):
        self.logger = logger
        self.conn = None
        self.device_id = str(get_mac())
        self.device_key = device_key

# Connect to the server
    def connect(self):
        while self.conn is None:
            try:
                self.conn = ssl.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                            keyfile="/etc/ssl/certs/key.pem",
                                            certfile="/etc/ssl/certs/cert.pem",
                                            cert_reqs=ssl.CERT_REQUIRED,
                                            ca_certs="/etc/ssl/certs/server_cert.pem",
                                            server_side=True
                                           )

                self.conn.connect((ServerConnection.SERVER_ADDR,
                                   ServerConnection.SERVER_PORT))
            except socket.error, msg:
                self.conn = None
                self.logger.error('Failed to connect to server. Retrying in 10 seconds..')
                self.logger.error('Error Message:' + str(msg))
                time.sleep(10)

    def send(self, data_dict):
        """
        Send some data to the server. The connection will be retried until the
        data is sent. Returns 1 for success, 0 for failure.
        """
        data_dict['device_key'] = self.device_key
        data_dict['device_id'] = self.device_id
        data = json.dumps(data_dict)

        while True:
            self.connect()

            try:
                self.conn.sendall(data)
                response = self.conn.recv(4096)
                d = json.loads(response)

                if 'flag' in d:
                    self.logger.info('Got flag "%s"' % d['flag'])
                    
                if 'error' in d:
                    self.logger.error('from server "%s"' % d['error'])

                return d['success']
            except socket.error:
                self.conn = None
            except (ValueError, TypeError, KeyError):
                # JSON decoding errors
                return 0

# Register this widget with the server
    def register_device(self):
        d = {'type' : 'register_device'}

        return self.send(d)

# Submit the PIN to the server for entry
    def open_door(self, pin):
        d = {'type' : 'open_door',
             'pin' : pin}

        return self.send(d)

# Alter the PIN for this widget
    def change_password(self, current_pin, new_pin):
        d = {'type' : 'tenant_change_password',
             'current_pin' : current_pin,
             'new_pin' : new_pin}

        return self.send(d)

# Change the master password for this widget
    def change_password_master(self, master_pin, new_pin):
        d = {'type' : 'master_change_password',
             'master_pin' : master_pin,
             'new_pin' : new_pin}

        return self.send(d)
