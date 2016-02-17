
#  1 Write 0x55AA to device
#  2 Check for I/O error (no device connected)
#  3 Read the device
#  4 Display result

# import libraries
import smbus as smbus
import fcntl

# define I2C address
i2c_addr = 0x48

#configure I2C bus for functions
i2c = smbus.SMBus(1)

# value to send
temp = 0x55AA

# Set outputs
try :
   print 'send write command'
   i2c.write_byte_data( i2c_addr, temp & 0xff, ( temp & 0xff ) >> 8 )
except IOError :
   print 'device not found at I2C address'
   error = 1
else :
   # Now read
   temp = i2c.read_word_data( i2c_addr, 0 )
   print 'we r reading'
