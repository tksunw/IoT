
### Setting up a ClusterHat v2 management network: 1 RPI 3 B+ with a ClusterHat, and 4 RPI Zero W.

#### Once Raspbian is installed on all 5:

----
##### Set up the Bridge on the contoller node:

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

You can use a bigger subnet than a /29, but since this is a ClusterHat, that can accomodate 4 Pi Zeroes, and the host Pi 3, so you don't need many IPs.  

##### On **all** the Pi Zeroes, update firmware, and enable USB Gadget mode networking and serial console:
* Update the firmware.  This is interactive, because you have to affirmatively confirm the update.
```
rpi-update
```

* Enable USB gadget mode networking and serial console:
```
echo dtoverlay=dwc2 >> /boot/config.txt
echo dwc2 >> /etc/modules
echo g_cdc >> /etc/modules
sudo systemctl enable getty@ttyGS0.service
```

* Configure the usb0 network interface on the pi zero at /etc/network/interfaces.d/usb0
```
auto usb0
iface usb0 inet static
    address 172.16.8.2
    netmask 255.255.255.248
    broadcast 172.16.8.7
```


