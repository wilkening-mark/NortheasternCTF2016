import time
import subprocess
import smbus


class AVRChip(object):
    """
    Class for communicating with the AVR on the CryptoCape. The AVR is
    responsible for reading characters from the keypad and controlling the
    status LED. On initialization this runs the "program_avr.sh" script, which
    verifies that the AVR is running the correct image, and loads the image if
    it isn't.
    """
    AVR_ADDR = 0x42

    def __init__(self):
        # Program the AVR. It has a tendency to fail without the delays here.
        time.sleep(5)
        subprocess.call('/usr/local/bin/program_avr.sh')
        time.sleep(5)
        self.bus = smbus.SMBus(1) # /dev/i2c-1

    def reset_keys(self):
        self.bus.write_byte(AVRChip.AVR_ADDR, 0x00)

    def read_key(self):
        return chr(self.bus.read_byte(AVRChip.AVR_ADDR))

    def led_on(self):
        self.bus.write_byte(AVRChip.AVR_ADDR, 0x02)

    def led_off(self):
        self.bus.write_byte(AVRChip.AVR_ADDR, 0x03)

    def avr_indicate_success(self):
        """
        Indicate a successful operation by turning on the LED for 3 seconds.
        """
        self.led_on()
        time.sleep(3)
        self.led_off()

    def avr_indicate_failure(self):
        """
        Indicate a failure by blinking the LED quickly 3 times.
        """
        for _ in range(3):
            self.led_on()
            time.sleep(0.3)
            self.led_off()
            time.sleep(0.3)
