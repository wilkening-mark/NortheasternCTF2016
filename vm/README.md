I've been using vagrant with a debian vm to run the server from, this seemed like a good way to keep track of what is going on in the server environment. I've just been running the server from /vagrant. There are a bunch of packages you need locally to run the server this should make it so anyone can plug in the beaglebone (provided they have the drivers) and then be able to run the server without having to mess with python or not having a linux to use it with

the startserver.sh file will start socat, the server, and netcat and show the output of netcat, while putting the output of the other two in a file

-Nick
