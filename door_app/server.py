from twisted.internet import reactor, protocol
from Crypto.PublicKey import RSA
from Crypto import Random
from datetime import datetime
import json
import os
import subprocess
from datetime import datetime

MASTER_PIN = '12345678'
REGISTERED_DEVICES = {}
PORT = 9500
# Note:  The port number for the server doesn't really matter since the "proxy" (socat) will be used to redirect the
# Widget traffic to wherever we want.   If you changed this port to 5000 and ran the server on the BeagleBone's host
# computer then you wouldn't need socat.  However, you should make sure that your system is tested with a proxy
# because it will be necessary for connecting to the live server.

DEFAULT_PIN = '654321'
DEFAULT_FLAG = 'Welcome Home, <tenant>'

ROOTDIR = os.path.dirname(__file__)
REGISTERED_FILE = os.path.join(ROOTDIR, 'registered-widgets.txt')
REQUESTED_FILE = os.path.join(ROOTDIR, 'requested-widgets.txt')

PRIVATE_KEY_FILE = '/Users/mwilkening/rsa_key'
private_key_f = open(PRIVATE_KEY_FILE, 'r')
private_key = RSA.importKey(private_key_f.read())
private_key_f.close()

class Widget(object):
    """
    Represents a Widget Device
    """

    def __init__(self, json_str):
        # Populate object attributes from JSON object
        # checks if valid JSON
        try:
            data = json.loads(json_str)
        except ValueError:
            raise ValueError('ValueError: Invalid JSON Values')

        # Cast device_id as type int, if fails, raise error
        try:
            self.device_id = int(data.get('device_id', None))
        except:
            raise TypeError('Cannot cast as int')

        # Cast pin as type int
        try:
            self.pin = int(data.get('pin', None))
        except:
            raise TypeError('Cannot cast as int')

        # Cast flag as type String
        try:
            self.flag = str(data.get('flag', None))
        except:
            raise TypeError('Cannot cast as String')

        # Checks device_key for type int
        try:
            self.device_key = int(data.get('device_key', None))
        except:
            raise TypeError('Cannot cast as int')


# TODO: Make this thread-safe and/or figure out what will happen when multiple requests come in simultaneously
class DoorServer(protocol.Protocol):
    """
    Handles incoming requests on TCP port.
    Expect request data to be formatted as:
        A header formatted as:
            'Special Byte' '0x00'
            Length of Message: 1 Byte
        A JSON object encrypted with device public key and signature:
            current_pin:  Sent with tenant_change_password request.
            device_id: <any unique identifier for the device>
            master_pin:   Sent with master_change_password request.
            new_pin:      Sent with tenant_change_password request.
            pin:   The pin encoded as ASCII -- only sent with 'open_door' request.
            timestamp: Time the message was encoded and sent
            type:     open_door | register_device | master_change_password | tenant_change_password

    Given that we are not opening new connections for incoming messages we are
    quite vulnerable to DOS. Not really a high priority though given the
    application.
    """

    """
    Buffer incoming message packets until we have a full message. If multiple
    messages are recieved simultaneously (very unlikely given normal operation)
    then those messages will not decrypt properly and will be discarded.
    """
    data_queue = ''
    message_length = 0

    # this function is called whenever we receive new data
    def dataReceived(self, data):

        try:
            request = json.loads(private_key.decrypt(data[2:message_length+2]))
            data = data[message_length+3:]
        except ValueError:
            # Bad data
            self.send_response(0)
            return

        # TODO:  Should verify that the json object has all the fields that we expect :)

        flag = None

        if (request["timestamp"] == self.get_bb_date()) and (request["timestamp"] == self.get_network_date()):
            if request["type"] == 'register_device':
                print "Register request (%s)" % repr(request)
                add_reg_request(request['device_key'], request['device_id'])
                self.send_response(1)
                return

            else:
                # For all requests other than register_device, we need to verify the device id and key
                if (request['device_id'] not in REGISTERED_DEVICES or
                    REGISTERED_DEVICES[request['device_id']].device_key != request['device_key']):
                    print "Denying request with invalid device_id or invalid device_key"
                    self.send_response(0)
                    return


            if request["type"] == 'open_door':
                print "Open door request (%s)" % repr(request)
                success, flag = verify_correct_pin(request['device_id'], request['pin'])

            elif request["type"] == 'master_change_password':
                print "PIN change request using master PIN (%s)" % repr(request)
                if request["master_pin"] == MASTER_PIN:
                    success = update_registered(request['device_id'], request['new_pin'])
                else:
                    success = 0

            elif request["type"] == 'tenant_change_password':
                print "Tenant PIN change request (%s)" % repr(request)
                success,_ = verify_correct_pin(request['device_id'], request['current_pin'])
                if success:
                    success = update_registered(request['device_id'], request['new_pin'])
            else:
                print "Unknown request (%s)" % repr(request)
                success = 0

            self.send_response(success, flag=flag)

        else:
            self.send_response(0)
            return


    # grabs timestamps from BB
    # formats to the same structure '%y%b%d%H:%M:%S'
    def get_bb_date(self):
        # Expected format: 'Tue Feb  9 21:28:23 UTC 2016'
        bb_date = subprocess.check_output(['date'])
        #the linux command will return an escape character at the end of the string, we don't want that
        bb_date = bb_date[0:28]

        # Format to '2016Feb0921:28:23'
        bb_date = datetime.strptime(bb_date, '%a %b %d %H:%M:%S %Z %Y')
        bb_date = datetime.strftime(bb_date, '%Y%b%d%H:%M:%S')

        return bb_date

    # grabs timestamps from network
    # formats to the same structure '%y%b%d%H:%M:%S'
    def get_network_date(self):
        # Expected format: 'Tue Feb  9 21:28:23 UTC 2016'
        network_date = subprocess.check_output(['ntpdate', '-q', 'time-c.nist.gov'])
        network_date = network_date[0:15]
        # network_date doesn't have a year, append to end
        network_date = network_date + ' 2016'

        # Format to '2016Feb0921:28:23' 
        network_date = datetime.strptime(network_date, '%d %b %H:%M:%S %Y')
        network_date = datetime.strftime(network_date, '%Y%b%d%H:%M:%S')

        return network_date

    def send_response(self, success, flag=None):
        """
        Send a response back to the Widget device with success value of 0 or 1
        and if success==1, then also send the flag
        """

        d = {'success' : success}
        # Add the flag if we have one and if we had success
        if success and flag is not None:
            d['flag'] = flag

        self.transport.write(json.dumps(d))



def update_registered(device_id,new_pin):
    """"
    Update the registered widget file (and working memory) with new pins.
    Returns success code (0 or 1).
    """

    if device_id not in REGISTERED_DEVICES:
        # This device isn't registered
        return 0

    # Update memory
    REGISTERED_DEVICES[device_id].pin = new_pin

    # Write updated devices back to disk
    with open(REGISTERED_FILE, 'w') as f:
        for (_, device) in REGISTERED_DEVICES.items():
            print >> f, json.dumps(device.__dict__)

    return 1


def add_reg_request(device_key, device_id):
    """
    Add registration request to requested-widgets file
    """

    d = {'device_id': device_id,
         'device_key' : device_key,
         'flag' : DEFAULT_FLAG,
         'pin'  : DEFAULT_PIN}

    with open(REQUESTED_FILE, 'a+') as f:
        print >> f, json.dumps(d)

    return d


def verify_correct_pin(device_id, pin):
    """
    Verify that the correct pin was sent for the given device_id.
    Returns tuple of (success_code, flag)
    """
    if device_id not in REGISTERED_DEVICES:
        # This device isn't registered
        return 0

    if REGISTERED_DEVICES[device_id].pin == pin:
        return (1, REGISTERED_DEVICES[device_id].flag)
    else:
        return (0, None)



def main():
    """
    Loads the registered-widgets file.
    Opens up ServerFactory to listen for requests on the specified port.
    """
    open(REGISTERED_FILE, 'a').close() # touch the file so that it exists

    with open(REGISTERED_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip lines that start with '#' so that we can comment-out lines
            if line.startswith('#'): continue
            print "Loading line: '%s'" % line

            new_widget = Widget(json_str=line)
            if new_widget.device_id in REGISTERED_DEVICES:
                print "Skipping duplicate device ID %s" % repr(new_widget.device_id)
            else:
                REGISTERED_DEVICES[new_widget.device_id] = new_widget

    factory = protocol.ServerFactory()
    factory.protocol = DoorServer
    print "Starting DoorApp server listening on port %d" % PORT
    reactor.listenTCP(PORT, factory)
    reactor.run()

if __name__ == '__main__':
    main()
