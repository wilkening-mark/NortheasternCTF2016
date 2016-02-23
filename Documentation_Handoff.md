#MITRE eCTF Challenge 2016
#Hand-off Document 2-24-16
##Northeastern Team
###Members: Benjamin Tan, Emily Pankosky, Erin O'Neill, Kim Tran, Mark Wilkening, Nicholas Kubasti, Samantha Gray, Victoria Suha  

---

##Irreversible Configurations Made  
The following changes were made in our BBB image :   
- We lock the ECC Chip  

---

##Master PIN  
Our default Master PIN has been set as `18981898`  
This pin is required to set a new Master PIN  
The process for setting a new Master PIN requires access to the server.  This is so no tenant can reset the Master PIN with just the widget.  

To set a new Master PIN:  
- Run `python change_master.py` from the same directory as the server.  
- Follow the prompts to enter the current and new PINs.  
- You will receive `Master PIN changed.  Please restart the server.` if the action was successful.  

---

##Image Install
Our Image can be written to an SD card, and when the BBB is booted from SD, the image will be installed on the BBB.  
We have attached the link to the image but it can also be found [here](link for the image file on Drive ?)   

---
Please contact us at [suha.v@husky.neu.edu](email:suha.v@husky.neu.edu) if any problems occur.  
Thank you!  
