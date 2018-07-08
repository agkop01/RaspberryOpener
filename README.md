# RaspberryOpener

Raspberry Opener allows to create server on Raspberry Pi having user accounts and login to them using application, thus each user can open or close the gate. Administrator of housing estate can add users to the server website. Everything done in the cheapest way. No expensive pilots, no expensive controllers.

This repository contains source code of the Web Application.

Android Application is available to download on [Google Play](https://play.google.com/store/apps/details?id=com.raspberryopener.app)

The source code of Android Application is available [here](https://github.com/orzechdev/raspberry-opener-android)


### Configuration on Raspberry

#### Installing necessary packages

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install bluetooth blueman bluez
```

Then reboot the Raspberry Pi:

```bash
sudo reboot
```

Next

```bash
sudo apt-get install python-bluetooth
sudo apt-get install python-rpi.gpio
sudo apt-get install python-pip python-dev ipython
sudo apt-get install bluetooth libbluetooth-dev
sudo pip install pybluez
sudo apt-get install python-django-extensions
sudo pip3 install django-extensions
```

And reboot the Raspberry Pi:

```bash
sudo reboot
```

#### Setup necessary SPP on the Pi

You'll first need to setup the SPP on the Pi. Edit this file:

```bash
sudo nano /etc/systemd/system/dbus-org.bluez.service 
```

Add ' -C' at the end of the 'ExecStart=' line, to start the bluetooth daemon in 'compatibility' mode. Add a new 'ExecStartPost=' immediately after that line, to add the SP Profile. The two lines should look like this:
```bash
ExecStart=/usr/lib/bluetooth/bluetoothd -C
ExecStartPost=/usr/bin/sdptool add SP
```

Save and reboot.

[Link with more information](https://www.raspberrypi.org/forums/viewtopic.php?p=919420#p919420)

#### Configuring Bluetooth Adapter

```bash
lsusb
sudo bluetoothctl
[bluetooth]# power on
[bluetooth]# agent off
[bluetooth]# agent DisplayOnly
[bluetooth]# discoverable on
[bluetooth]# pairable on
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

#### Additional helpful sources

[Controlling Raspberry Pi GPIO using Android App over Bluetooth](https://circuitdigest.com/microcontroller-projects/controlling-raspberry-pi-gpio-using-android-app-over-bluetooth)

[Android Linux / Raspberry Pi Bluetooth communication](http://blog.davidvassallo.me/2014/05/11/android-linux-raspberry-pi-bluetooth-communication/)

[Great example of Bluetooth chat service in Android](https://github.com/googlesamples/android-BluetoothChat/blob/master/Application/src/main/java/com/example/android/bluetoothchat/BluetoothChatService.java)

