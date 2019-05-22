
### Setting up ClusterHat v2 networking on 1 RPI 3 B+, with a ClusterHat, and 4 RPI Zero W.

#### Once Raspbian is installed on all 5:

----
#####Set up the Bridge on the contoller node:

Install the `bridge-utils` package:
```
apt-get install bridge-utils
```

Create the bridge:
```
brctl addbr br0
```

Create the file: /etc/network/interfaces.d/br0 with the contents:
```
auto br0
iface br0 inet static
    ipaddress 172.16.244.1
    netmask 255.255.255.248
    broadcast 172.16.244.7
    bridge_ports usb0 usb1 usb2 usb3
```

On **all** the Pi Zeroes, update firmware, and enable USB Gadget mode networking and serial console:
* Update the firmware.  This is interactive, because you have to affirmatively confirm the update.
```
rpi-update
```


