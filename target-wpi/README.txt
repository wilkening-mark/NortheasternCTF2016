	
	
This target contains the following:
    bbb.img - BeagleBone SDCard image (will overwrite eMMC during first boot)
    packet-captures - Directory containing packet captures that can be analyzed with WireShark.
		These captures are for widgets that are registered on the live server for the "Master PIN", 
		"Shoulder Surfing", and "New Neighbor" flags, as described in section 5.1 of challenge 
		description doc.
    src - Source code for the widget.

Special Instructions:
    * Sometimes the keypad can be a little finicky, so watch the green LED on
      the CryptoCape when you're entering values. It should blink once for each
      key-press, and blink 3 times quickly when you enter something invalid.
      Often it thinks the first press of a new PIN is invalid, so just wait for
      it to stop blinking and try again.

    * The debug port (6000) isn't great at dealing with multiple connections.
      Sometimes only the first connection works, but if this happens it can be
      fixed by resetting the widget.

    * If the widget can't connect to the server, the green LED on the
      CryptoCape turns on and doesn't turn off until the connection is
      successful. No log message is printed, so this can be confusing.


	
Documentation:

--------------
Introduction
--------------
In this document, we will explain the basic functionality of the server, how it interacts with the 
other components of the system (Widget), and a little about what is in the different source files.

--------------
Image Setup
--------------
Load image (bbb.img) onto an SD card.  Load by pressing button near SD card on boot, AVR
programming is automatic upon the first boot.


--------------
Registration
--------------
Server receives public key from the ARM. Then authentication protocol setup is done via sharing 
secrets and storing them for future reference.

--------------
Unlock
--------------
Server receives unlock request from the widget, then replies with a challenge. Afterwards server 
receives a package from the widget containing the pin. Server responds with message indicating 
success/failure.


ARM Python Code Overview
--------------
Introduction
--------------
In this part of the documentation, the basic functionality of the Python codes ran on the ARM 
processor is explained including specifications for LED response during registration, unlock, and 
changepin. The ARM is also configured so that upon the first boot of the system after the image is 
loaded, it will flash the AVR. The only requirement is that the original bootloader for the 
cryptocape AVR is flashed and everthing will work properly.
The ARM will send data to and process data from the server. Upon a succesful request the LED on the 
BB will turn LED for 3 seconds. Upon an invalid request it will blink. 3 times.

--------------
Registration
--------------
The ARM will generate oublic private key and send it to AVR and server. Then authentication 
protocol setup is done by sharing secrets.

The ARM polls AVR in order to find out the unlock request. Then it forwards the request to server. 
After receiving challenge from server, ARM forwards it to the AVR. ARM waits until AVR computes the 
hash of the challenge and the pin. ARM receives the package and forwards it to the server.

--------------
Change Pin
--------------
The ARM will poll AVR in order to initiate change pin operation. Change pin protocol follows exact 
same flow as the unlock process. ARM acts as an intermediate messanger between AVR and the server.



AVR C Code Overview
--------------
Introduction
--------------
The AVR reads keys from the keypad, performs SHA hashing and HMAC. These functions are combined to 
achieve the security protocol. All outside communication is performed through external polling of 
the “currstatus”, which in turn may result in specific external requests that call internal code to 
carry out crypto.

--------------
Keypad I/O
--------------
The code for reading the keypad is identical to the stock solution. The keypad is polled from 
within a forever loop. If a keypress is detected, the LED is flashed. Then, the keypress is stored 
in a buffer. If the key pressed is pound (#), then the keybuffer is checked to see what command 
(or partial command) has been entered and if it is valid. The check is performed first by the 
number of characters entered, then by verifying the presence of special characters. After verifying 
any particular command, the status is set appropriately.

--------------
Registration
--------------
During registration, the AVR obtains a secret (generated externally). The registration keypad 
sequence is detected and status is set for registration. Via polling, the registration is 
propagated. Registration is completed when the secret is done being copied onto the AVR.

--------------
Unlock
--------------
During unlock, the user’s pin is securely communicated externally. When the keypad sequence for 
unlock is detected, the status is set. The AVR will wait to be polled and then communicate the 
unlock status. After some time, a challenge is sent to the AVR. The challenge is combined with the 
pin entered, hashed, and then status is once again set. The AVR waits to be polled, then 
communicates the hash. Unlock is completed after the hash is communicated.
The code to flash the LED (access granted/denied) is called externally.

--------------
Change Pin
--------------
During pin change, the a large combination of crypto operations are performed to securely 
communicate the new pin externally. When the keypad sequence for either type of pin change is 
detected, the status is set. The AVR will wait to be polled and then communicate the pin change 
status. After some time, a challenge is sent to the AVR. The challenge is combined with the old 
pin or master pin, hashed. The new pin is hashed then mixed with the hmac of the secret and hash 
of the old pin. The old/master pin is concatenated with the challenge, then hashed. Both of these 
packages are concatenated then this final package is ready to polled by the ARM. Pin Change is 
completed after the digest is communicated to the server.

