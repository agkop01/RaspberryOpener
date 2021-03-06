from bluetooth import *
import bluetooth, subprocess
import socket
from django.contrib.auth.models import User
from time import sleep
import time
import threading
# TODO -> Uncomment On Raspberry: import RPi.GPIO as GPIO


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
    SEND_OBSTACLE = "obstacle"
    SEND_OBSTACLE_REMOVED = "obstacleRemoved"

    PIN_MOTOR_A = 16
    PIN_MOTOR_B = 18
    PIN_MOTOR_ENABLE = 22
    gate_opened = False
    gate_closed = True
    PIN_SENSOR_OBSTACLE = 21
    TRIG = 11  # 23 GPIO.setmode(GPIO.BCM)
    ECHO = 13  # 24 GPIO.setmode(GPIO.BCM)

    client_sock = None
    password_correct = False
    is_checking_distance = False
    distance = 1000
    thread_check = None

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

            # TODO -> Uncomment On Raspberry: GPIO.setup(self.PIN_MOTOR_A, GPIO.OUT)
            # TODO -> Uncomment On Raspberry: GPIO.setup(self.PIN_MOTOR_B, GPIO.OUT)
            # TODO -> Uncomment On Raspberry: GPIO.setup(self.PIN_MOTOR_ENABLE, GPIO.OUT)
            # TODO -> Uncomment On Raspberry: GPIO.setup(self.PIN_SENSOR_OBSTACLE, GPIO.IN)
            # TODO -> Uncomment On Raspberry: GPIO.setup(self.TRIG, GPIO.OUT)
            # TODO -> Uncomment On Raspberry: GPIO.setup(self.ECHO, GPIO.IN)

            # passkey = "1234" # passkey of the device you want to connect

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

            # threading.Thread(target=self.on_obstacle_detected).start()
            # threading.Thread(target=self.on_obstacle_removed).start()

            self.start_service(server_sock, port)

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

                    if data_received[0:6] == 'login=':
                        data_arr = data_received[6:].split('&pass=')
                        if len(data_arr) == 2 and len(data_arr[0]) > 0 and len(data_arr[1]) > 0:
                            self.password_correct = False
                            try:
                                user = User.objects.get(username=data_arr[0])
                                print("Username exists")
                                self.password_correct = user.check_password(data_arr[1])
                                if self.password_correct:
                                    print("Password is correct")
                                    data_gate_info = ""
                                    if self.gate_opened:
                                        data_gate_info = "&" + self.SEND_GATE_OPENED
                                    if self.gate_closed:
                                        data_gate_info = "&" + self.SEND_GATE_CLOSED
                                    self.send_data(self.client_sock, self.SEND_LOGIN_CORRECT + data_gate_info)
                                else:
                                    print("Password is wrong")
                                    self.send_data(self.client_sock, self.SEND_LOGIN_WRONG_PASSWORD)
                            except User.DoesNotExist:
                                # Create a new user. There's no need to set a password
                                # because only the password from settings.py is checked.
                                print("Username do not exists")
                                self.send_data(self.client_sock, self.SEND_LOGIN_WRONG_USERNAME)
                            
                            if self.password_correct:
                                while True:
                                    data_received_2 = self.client_sock.recv(1024).decode("utf-8")
                                    print("received2 [%s]" % data_received_2)

                                    if data_received_2 == 'openGate':
                                        if not self.gate_opened:
                                            self.open_gate()
                                            self.gate_closed = False
                                            self.send_data(self.client_sock, self.SEND_GATE_OPENING)
                                            sleep(2)
                                            self.stop_motor()
                                            self.gate_opened = True
                                            self.send_data(self.client_sock, self.SEND_GATE_OPENED)
                                        else:
                                            self.send_data(self.client_sock, self.SEND_GATE_OPENED)
                                    elif data_received_2 == 'closeGate':
                                        if not self.gate_closed:
                                            if self.thread_check is None or not self.thread_check.isAlive():
                                                self.thread_check = None
                                                self.send_data(self.client_sock, self.SEND_GATE_CLOSING)
                                                obstacle = self.is_obstacle_present()
                                                if not obstacle:
                                                    self.close_gate()
                                                    self.gate_opened = False
                                                    self.send_data(self.client_sock, self.SEND_GATE_CLOSING)
                                                    sleep(2)
                                                    self.stop_motor()
                                                    self.gate_closed = True
                                                    self.send_data(self.client_sock, self.SEND_GATE_CLOSED)
                                                else:
                                                    self.send_data(self.client_sock, self.SEND_OBSTACLE)
                                            else:
                                                self.send_data(self.client_sock, self.SEND_OBSTACLE)
                                        else:
                                            self.send_data(self.client_sock, self.SEND_GATE_CLOSED)
                                    elif data_received_2[0:7] == 'endConn':
                                        break
                                    else:
                                        self.send_data(self.client_sock, "wrongSecondInput")

                        else:
                            self.send_data(self.client_sock, self.SEND_LOGIN_WRONG_DATA)
                            print("Username and/or password are not accepted")

                    elif data_received[0:7] == 'endConn':
                        break

                    else:
                        self.send_data(self.client_sock, "wrongFirstInput")

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
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_A, GPIO.HIGH)
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_B, GPIO.LOW)
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_ENABLE, GPIO.HIGH)
        return

    def close_gate(self):
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_A, GPIO.LOW)
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_B, GPIO.HIGH)
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_ENABLE, GPIO.HIGH)
        return

    def stop_motor(self):
        # TODO -> Uncomment On Raspberry: GPIO.output(self.PIN_MOTOR_ENABLE, GPIO.LOW)
        return

    # def on_obstacle_detected(self):
    #     while True:
    #         # Wait for changing state of sensor from low to high
    #         # TODO -> Uncomment On Raspberry: GPIO.wait_for_edge(self.PIN_SENSOR_OBSTACLE, GPIO.RISING)
    #         # Obstacle detected
    #         # Sending information that obstacle is detected only if gate is opened
    #         if self.client_sock is not None and self.password_correct and self.gate_opened:
    #             data_to_send = self.SEND_OBSTACLE
    #             self.send_data(self.client_sock, data_to_send)
    #             print("on_obstacle_detected - send to device")

    # def on_obstacle_removed(self):
    #     while True:
    #         # Wait for changing state of sensor from high to low
    #         # TODO -> Uncomment On Raspberry: GPIO.wait_for_edge(self.PIN_SENSOR_OBSTACLE, GPIO.FALLING)
    #         # Obstacle removed
    #         # Sending information that obstacle was removed and sending current state
    #         if self.client_sock is not None and self.password_correct:
    #             data_to_send = self.SEND_OBSTACLE_REMOVED
    #             if self.gate_opened:
    #                 data_to_send += "&" + self.SEND_GATE_OPENED
    #             elif self.gate_closed:
    #                 data_to_send += "&" + self.SEND_GATE_CLOSED
    #             self.send_data(self.client_sock, data_to_send)
    #             print("on_obstacle_removed - send to device")

    def on_obstacle_removed(self):
        while True:
            is_obstacle = self.is_obstacle_present()
            if is_obstacle:
                continue
            else:
                if self.client_sock is not None and self.password_correct:
                    data_to_send = self.SEND_OBSTACLE_REMOVED
                    if self.gate_opened:
                        data_to_send += "&" + self.SEND_GATE_OPENED
                    elif self.gate_closed:
                        data_to_send += "&" + self.SEND_GATE_CLOSED
                    self.send_data(self.client_sock, data_to_send)
                    print("on_obstacle_removed - send to device")
                self.thread_check = None
                break

    pulse_end = 1  # TODO smth

    def is_obstacle_present(self):
        self.pulse_end  # TODO smth = 2
        pulse_start = 1

        # TODO -> Uncomment On Raspberry: GPIO.output(self.TRIG, False)
        print("check_distance checking...")
        time.sleep(2)

        # TODO -> Uncomment On Raspberry: GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        # TODO -> Uncomment On Raspberry: GPIO.output(self.TRIG, False)

        # TODO -> Uncomment On Raspberry: while GPIO.input(self.ECHO) == 0:
        # TODO -> Uncomment On Raspberry:     pulse_start = time.time()

        # TODO -> Uncomment On Raspberry: while GPIO.input(self.ECHO) == 1:
        # TODO -> Uncomment On Raspberry:     pulse_end = time.time()

        pulse_duration = self.pulse_end - pulse_start  # TODO smth

        distance = pulse_duration * 17150

        distance = round(distance, 2)
        print("check_distance: " + str(distance))

        self.pulse_end += 1  # TODO smth

        if distance < 20:
            if self.thread_check is None or not self.thread_check.isAlive():
                self.thread_check = threading.Thread(target=self.on_obstacle_removed)
                self.thread_check.start()
            return True
        else:
            return False


def run():
    BluetoothServiceSingleton.get_instance()

