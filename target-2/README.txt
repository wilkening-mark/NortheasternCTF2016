This target contains the following:

	bbb.img - BeagleBone eMMC flasher image. (This will self-install/overwrrite the eMMC on the BBB)
	
	packet-captures - 
		Packet captures of widgets that are registered on the live server for the "Master PIN", 
		"Shoulder Surfing", and "New Neighbor" flags, as described in section 5.1 of challenge 
        description doc.  Note:  the flags were all changed after collecting the packet captures, 
        so any flag values observed (e.g. in debug traffic to port 6000) are no longer valid.  If you
        open the door you will reveal the updated flag.
		Packet captures can be opened/analyzed with WireShark.
		
	src - Source code for the widget.

Special instructions:
    * Everything on the BeagleBone should run automatically at startup.
	* The BeagleBone image makes no one-way hardware modifications.
