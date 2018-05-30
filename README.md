# RaspberryOpener
Web app

### Configuration on Raspberry

#### Configuring Bluetooth Adapter

```bash
lsusb
sudo bluetoothctl
[bluetooth]# power on
[bluetooth]# agent on
[bluetooth]# discoverable on
[bluetooth]# pairable on
[bluetooth]# scan on
```

#### Running Service

```bash
sudo python3 tempBluetoothFile.py
```
