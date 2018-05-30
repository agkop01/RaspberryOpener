# RaspberryOpener
Web app

### Configuration on Raspberry

#### Installing necessary packages

```bash
sudo apt-get install python-django-extensions
sudo pip3 install django-extensions
```

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

After starting Django server, i.e.:

```bash
sudo python3 manage.py runserver
```

We can start bluetooth service to communicate with Android App:

```bash
sudo python3 manage.py runscript bluetooth_service
```
