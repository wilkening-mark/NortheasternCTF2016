#  Write 0x55AA to device

# import libraries
# from Adafruit_I2C import Adafruit_I2C
from Crypto.PublicKey import RSA
import smbus as smbus
import fcntl
import time

# define I2C address
i2c_addr = 0x42

#configure I2C bus for functions
i2c = smbus.SMBus(1) # /dev/i2c-1

# values to send
low = 0x00

# generate a key to write
PUBLIC_KEY_FILE = '/home/debian/rsa_key.pub'
public_key_f = open(PUBLIC_KEY_FILE, 'r')
public_key_r = public_key_f.read()
public_key = RSA.importKey(public_key_r)
public_key_f.close()
b = bytearray()
b.extend(public_key_r.encode())

# Set outputs
try :
   print 'wake up chip by sending low'
   # send low
   i2c.write_byte(i2c_addr, low)
   print '1'
   i2c.write_byte(i2c_addr, low)
   print '2'
   i2c.write_byte(i2c_addr, low)
   print '3'
   # i2c.write8(i2c_addr, low)
   time.sleep(1) # wait
   print 'attempt to write ' + str(public_key_r)
   # write data in 32 byte increments
   for x in range(3):
       lower = 0 + (32 * x)
       upper = 32 + (32 * x)
       if x == 0:
           print list(b[lower : upper])
           i2c.write_i2c_block_data(i2c_addr, 0, list(b[lower : upper])) # write data
       elif x == 1:
           print list(b[lower : upper])
           i2c.write_i2c_block_data(i2c_addr, 0, list(b[lower : upper])) # write data
       elif x == 2:
           print list(b[lower : upper])
           i2c.write_i2c_block_data(i2c_addr, 0, list(b[lower : upper])) # write data
       #i2c.write_i2c_block_data(i2c_addr, 0, b[lower : upper])
   print 'reading what we wrote'

   for x in range(3):
       if x == 0:
           r = i2c.read_i2c_block_data(i2c_addr, 32)
           print list(r)
       elif x == 1:
           r = i2c.read_i2c_block_data(i2c_addr, 32)
           print list(r)
       elif x == 2:
           r = i2c.read_i2c_block_data(i2c_addr, 32)
           print list(r)
       #i2c.write_i2c_block_data(i2c_addr, 0, b[lower : upper])


   # r = i2c.readList(i2c_addr, 416)

except IOError :
   print 'device not found at I2C address'
   error = 1
else :
   # i2c.read_i2c_block_data(i2c_addr, 0)
   print 'end'
