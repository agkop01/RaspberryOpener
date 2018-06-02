from bluetooth import *
import bluetooth, subprocess
import socket
from django.contrib.auth.models import User
from threading import Thread
# from models import User


class BluetoothServiceSingleton:
    # Here will be the instance stored.
    __instance = None

    SEND_LOGIN_CORRECT = "loginStatus=1"
    SEND_LOGIN_WRONG_PASSWORD = "loginStatus=-1"
    SEND_LOGIN_WRONG_USERNAME = "loginStatus=-2"
    SEND_LOGIN_WRONG_DATA = "wrongUserData"
    SEND_GATE_OPENING = "openingGate"
    SEND_GATE_CLOSING = "closingGate"
    SEND_GATE_OPENED = "gateIsOpened"
    SEND_GATE_CLOSED = "gateIsClosed"

    PIN_OPEN_GATE = 16
    PIN_CLOSE_GATE = 17
    PIN_IS_GATE_OPENED = 18
    PIN_IS_GATE_CLOSED = 19

    client_sock = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if BluetoothServiceSingleton.__instance == None:
            BluetoothServiceSingleton()
        return BluetoothServiceSingleton.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if BluetoothServiceSingleton.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            BluetoothServiceSingleton.__instance = self

            passkey = "1234" # passkey of the device you want to connect

            # kill any "bluetooth-agent" process that is already running
            #print("subprocess 1")
            #subprocess.call("kill -9 `pidof bluetooth-agent`",shell=True)
            #print("subprocess 2")

            # Start a new "bluetooth-agent" process where XXXX is the passkey
            #print("subprocess 3")
            #status = subprocess.call("bluetooth-agent " + passkey + " &",shell=True)
            #print("subprocess 4")

            server_sock = BluetoothSocket(RFCOMM)
            server_sock.bind(("", PORT_ANY))
            server_sock.listen(1)

            port = server_sock.getsockname()[1]

            uuid = "00001101-0000-1000-8000-00805f9b34fb"

            advertise_service(server_sock, "AquaPiServer",
                              service_id=uuid,
                              service_classes=[uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE],
                              # protocols = [ OBEX_UUID ]
                              )

            self.start_service(server_sock, port)

            thread_on_gate_opened = Thread(target=self.on_gate_opened, args=())
            thread_on_gate_closed = Thread(target=self.on_gate_closed, args=())
            thread_on_gate_opened.start()
            thread_on_gate_closed.start()

    def start_service(self, server_sock, port):
        while True:
            print("Waiting for connection on RFCOMM channel %d" % port)

            self.client_sock, client_info = server_sock.accept()
            print("Accepted connection from ", client_info)
            #self.client_sock.settimeout(60.0)

            try:
                while True:
                    data_received = self.client_sock.recv(1024).decode("utf-8")
                    print("received [%s]" % data_received)
                    # if len(data_received) == 0:
                    #     break

                    data_to_send = ""

                    if data_received[0:6] == 'login=':
                        data_arr = data_received[6:].split('&pass=')
                        if len(data_arr) == 2 and len(data_arr[0]) > 0 and len(data_arr[1]) > 0:
                            password_correct = False
                            try:
                                user = User.objects.get(username=data_arr[0])
                                print("Username exists")
                                password_correct = user.check_password(data_arr[1])
                                if password_correct:
                                    print("Password is correct")
                                    data_to_send = self.SEND_LOGIN_CORRECT
                                else:
                                    print("Password is wrong")
                                    data_to_send = self.SEND_LOGIN_WRONG_PASSWORD
                            except User.DoesNotExist:
                                # Create a new user. There's no need to set a password
                                # because only the password from settings.py is checked.
                                print("Username do not exists")
                                data_to_send = self.SEND_LOGIN_WRONG_USERNAME

                            self.send_data(self.client_sock, data_to_send)
                            
                            if password_correct:
                                while True:
                                    data_received_2 = self.client_sock.recv(1024).decode("utf-8")
                                    print("received2 [%s]" % data_received_2)
                                    data_to_send_2 = ""

                                    if data_received_2 == 'openGate':
                                        if not self.is_gate_opened:
                                            self.open_gate()
                                            data_to_send_2 = self.SEND_GATE_OPENING
                                        else:
                                            data_to_send_2 = self.SEND_GATE_OPENED
                                    elif data_received_2 == 'closeGate':
                                        if not self.is_gate_closed:
                                            self.close_gate()
                                            data_to_send_2 = self.SEND_GATE_CLOSING
                                        else:
                                            data_to_send_2 = self.SEND_GATE_CLOSED
                                    elif data_received_2[0:7] == 'endConn':
                                        break

                                    self.send_data(self.client_sock, data_to_send_2)
                                    print(data_to_send_2)

                        else:
                            data_to_send = self.SEND_LOGIN_WRONG_DATA
                            self.send_data(self.client_sock, data_to_send)
                            print("Username and/or password are not accepted")

                    elif data_received[0:7] == 'endConn':
                        break

                    else:
                        data_to_send = 'wrongInput'
                        self.send_data(self.client_sock, data_to_send)
                        print("Wrong input")

            except IOError:
                print("IOError")
                pass

            except KeyboardInterrupt:
                print("KeyboardInterrupt")

                print("disconnected")

                self.client_sock.close()
                server_sock.close()
                self.client_sock = None
                print("all done")

                break

    def send_data(self, client_sock, data_to_send):
        client_sock.send(data_to_send)
        print("Sending [%s]" % data_to_send)

    def open_gate(self):
        # GPIO.output(self.PIN_CLOSE_GATE, False)
        # GPIO.output(self.PIN_OPEN_GATE, True)
        return

    def close_gate(self):
        # GPIO.output(self.PIN_OPEN_GATE, False)
        # GPIO.output(self.PIN_CLOSE_GATE, True)
        return

    def is_gate_opened(self):
        # TODO Checking opening limit switch
        # return GPIO.input(self.PIN_IS_GATE_OPENED)
        return False

    def is_gate_closed(self):
        # TODO checking closing limit switch
        # return GPIO.input(self.PIN_IS_GATE_CLOSED)
        return False

    def on_gate_opened(self):
        while True:
            # TODO 1. Wait for changing state of opening limit switch from low to high
            #
            # GPIO.wait_for_edge(self.PIN_IS_GATE_OPENED, GPIO.RISING)
            # Opening limit switch triggered
            #
            # TODO 2. Code to physically stop opening gate
            #
            # GPIO.output(self.PIN_OPEN_GATE, False)
            #
            # 3. Sending information about gate opened to device if exists
            if self.client_sock is not None:
                data_to_send = self.SEND_GATE_OPENED
                self.send_data(self.client_sock, data_to_send)
                print("on_gate_opened - send to device")

    def on_gate_closed(self):
        while True:
            # TODO 1. Wait for changing state of closing limit switch from low to high
            #
            # GPIO.wait_for_edge(self.PIN_IS_GATE_CLOSED, GPIO.RISING)
            # Closing limit switch triggered
            #
            # TODO 2. Code to physically stop closing gate
            #
            # GPIO.output(self.PIN_CLOSE_GATE, False)
            #
            # 3. Sending information about gate closed to device if exists
            if self.client_sock is not None:
                data_to_send = self.SEND_GATE_CLOSED
                self.send_data(self.client_sock, data_to_send)
                print("on_gate_opened - send to device")


def run():
    BluetoothServiceSingleton.get_instance()

