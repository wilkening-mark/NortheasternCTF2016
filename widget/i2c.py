#  Write 0x55AA to device

# import libraries
import smbus as smbus
import fcntl
import time

# define I2C address
i2c_addr = 0x48

#configure I2C bus for functions
i2c = smbus.SMBus(1) # /dev/i2c-1

# values to send
temp = 0x55AA
low = 0x00

# Set outputs
try :
   print 'wake up chip!!'
   # send low
   i2c.write_byte(i2c_addr, low)
   time.sleep(1) # wait
   print 'attempt to write'
   i2c.write_byte_data( i2c_addr, temp & 0xff, ( temp & 0xff ) >> 8 ) # write data

except IOError :
   print 'device not found at I2C address'
   error = 1
else :
   # Now read
   temp = i2c.read_word_data( i2c_addr, 0 )
   print 'we r reading'
