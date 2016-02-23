from twisted.internet import reactor, protocol
from Crypto.PublicKey import RSA
from Crypto import Random
from datetime import datetime
import json
import os
import subprocess
import Queue
from datetime import datetime
from collections import deque
import struct
import sys

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
REGISTERED_FILE = os.path.join(ROOTDIR, 'data', 'registered-widgets.txt')
REQUESTED_FILE = os.path.join(ROOTDIR, 'data', 'requested-widgets.txt')

PRIVATE_KEY_FILE = '/Users/mwilkening/rsa_key'
private_key_f = open(PRIVATE_KEY_FILE, 'r')
private_key = RSA.importKey(private_key_f.read())
private_key_f.close()

# Needed to solve unicode problems on Mac
def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string
    # representation
    if isinstance(data, unicode):
        try:
            return int(data.encode('utf-8'))
        except ValueError:
            return data.encode('utf-8')
    # if this is a list of values, return
    # list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a
    # dictionary, return
    # dictionary of byteified
    # keys and values
    # but only if we
    # haven't already byteified
    # it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

class Widget(object):
    """
    Represents a Widget Device
    """

    def __init__(self, json_str):
        # Populate object attributes from JSON object
        # checks if valid JSON
        try:
            data = json_loads_byteified(json_str)
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
    data_queue = bytearray('')
    message_length = 0

    def __init__(self):
        self.timeQueue = TimeQueue()

    # this function is called whenever we receive new data
    def dataReceived(self, data):

        if self.timeQueue.rate_limit_full():
            print "Rate limit reached."
            self.send_response(0)
            return

        self.data_queue += bytearray(data)
        if struct.unpack("I", bytes(self.data_queue[0:4]))[0] == 0:
            self.message_length = struct.unpack("I", bytes(self.data_queue[4:8]))[0]
        else:
            # Bad data
            self.send_response(0)
            return

        if sys.getsizeof(self.data_queue) < self.message_length + 8:
            return

        try:
            request = json_loads_byteified(private_key.decrypt(
                bytes(self.data_queue[8:self.message_length+8])))
            self.data_queue = self.data_queue[self.message_length+8:]
        except ValueError:
            # Bad data
            self.send_response(0)
            return

        # TODO:  Should verify that the json object has all the fields that we expect :)

        flag = None
        
        ##nick adding signature check
        signature = request['signature']
        pubKey = request['pubKey']
        del request['signature']
        del request['pubKey']
        with open('datas','w+') as f:
            json.dump(request,f)
        isFail=subprocess.check_output(['eclet','offline-verify-sign','-f','datas','--signature',signature,'--public-key',pubKey])
        if isFail is not None:
            self.send_response(0)
            print 'signature failed'
            return  
        
        if True: #(request["timestamp"] == self.get_bb_date()) and (request["timestamp"] == self.get_network_date()):
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

class TimeQueue(object):
    def __init__(self):
        """
        Creates a table that lists the last attempts to unlock the door.
        This table stores the times to limit the possibility of brute force.
        """
        self.REQUEST_LIMIT_PER_TIME = 60
        self.HOURS = 1.0
        self.MINUTES_IN_HOUR = 60
        self.SECONDS_IN_MINUTE = 60

        self.access_table = deque()

    def push_access_time(self):
        now = datetime.now()
        #print now
        self.access_table.append(now)

    def rate_limit_full(self):
        """
        Checks the amount of unlocks that have been done in the last hour,
        removing them from the queue if they are older. If fewer than the limit
        (the size of the queue) have been done, goes through with the unlock if valid.
        """


        if len(self.access_table) >= self.REQUEST_LIMIT_PER_TIME:
            now = datetime.now()
            then = self.access_table[0]

            while len(self.access_table) > 0 and \
                abs(now - then).total_seconds() > \
                self.HOURS * self.MINUTES_IN_HOUR * self.SECONDS_IN_MINUTE:

                #current = self.access_table[0]
                #print "Current:" + str(current)

                if len(self.access_table) > 0:
                    then = self.access_table.popleft()

                #print len(self.access_table)

                #sprint abs(now - then).total_seconds()

            if len(self.access_table) >= self.REQUEST_LIMIT_PER_TIME:
                return True
            else:
                self.push_access_time()
                return False

        else:
            self.push_access_time()
            return False


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
