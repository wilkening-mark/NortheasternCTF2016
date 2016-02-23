import os, sys, getpass, hashlib

master_path = "data/.yolo"
default_password = "18981898"

# If yolo file exists, read master pin's hash from it
if os.path.exists(master_path):
    with open(master_path) as f:
        MASTER_PIN = f.readline().strip()
# Otherwise, create it with the hash from default_password
else:
    with open(master_path, 'w') as f:
        MASTER_PIN = hashlib.sha224(default_password).hexdigest()
        f.write(MASTER_PIN)

#print "Args:", len(sys.argv), str(sys.argv)

# If we run "python change_master.py" we can change the password
old_pin = getpass.getpass("Enter current master PIN:")

new_pin = getpass.getpass("Enter new master PIN:")
confirm_pin = getpass.getpass("Confirm new master PIN:")

if new_pin != confirm_pin:
    print "New PINs did not match."
    quit()

for i in new_pin:
    if not i.isdigit():
        print "New PIN contains invalid character(s)."
        quit()

if len(new_pin) != 8:
    print "New PIN length invalid."
    quit()

if hashlib.sha224(old_pin).hexdigest() == MASTER_PIN:
    NEW_MASTER = hashlib.sha224(new_pin).hexdigest()
    with open(master_path, 'w') as f:
        f.write(NEW_MASTER)
    print "Master PIN changed. Please restart the server."
    quit()
else:
    print "Incorrect PIN."
    quit()