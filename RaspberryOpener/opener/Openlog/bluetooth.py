from bluetooth import *
import bluetooth, subprocess
# from models import User


class BluetoothServiceSingleton:
    # Here will be the instance stored.
    __instance = None

    OPENING_PIN = 16
    CLOSING_PIN = 17

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

    def start_service(self, server_sock, port):
        while True:
            print("Waiting for connection on RFCOMM channel %d" % port)

            client_sock, client_info = server_sock.accept()
            print("Accepted connection from ", client_info)

            try:
                while True:
                    data_received = client_sock.recv(1024)
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
                                    data_to_send = "loginStatus=1"
                                else:
                                    print("Password is wrong")
                                    data_to_send = "loginStatus=-1"
                            except User.DoesNotExist:
                                # Create a new user. There's no need to set a password
                                # because only the password from settings.py is checked.
                                print("Username do not exists")
                                data_to_send = "loginStatus=-2"

                            self.send_data(client_sock, data_to_send)
                            
                            if password_correct:
                                while True:
                                    data_received_2 = client_sock.recv(1024)
                                    data_to_send_2 = ""

                                    if data_received_2 == 'openGate':
                                        self.open_gate()
                                        data_to_send_2 = 'openingGate'
                                    elif data_received_2 == 'closeGate':
                                        self.close_gate()
                                        data_to_send_2 = 'closingGate'
                                    elif data_received[0:7] == 'endConn':
                                        break

                                    self.send_data(client_sock, data_to_send_2)

                        else:
                            data_to_send = 'wrongUserData'
                            self.send_data(client_sock, data_to_send)

                    elif data_received[0:7] == 'endConn':
                        break

                    else:
                        data_to_send = 'wrongInput'
                        self.send_data(client_sock, data_to_send)

            except IOError:
                pass

            except KeyboardInterrupt:

                print("disconnected")

                client_sock.close()
                server_sock.close()
                print("all done")

                break

    def send_data(self, client_sock, data_to_send):
        client_sock.send(data_to_send)
        print("Sending [%s]" % data_to_send)

    def open_gate(self):
        if not self.is_gate_opened:
            # GPIO.output(self.OPENING_PIN, True)
            # GPIO.output(self.CLOSING_PIN, False)
            pass

    def close_gate(self):
        if not self.is_gate_closed:
            # GPIO.output(self.OPENING_PIN, False)
            # GPIO.output(self.CLOSING_PIN, True)
            pass

    def is_gate_opened(self):
        # TODO checking opening limit switch
        return False

    def is_gate_closed(self):
        # TODO checking closing limit switch
        return False

    def on_gate_opened(self):
        # TODO opening limit switch triggered
        # GPIO.output(self.OPENING_PIN, False)
        pass

    def on_gate_closed(self):
        # TODO closing limit switch triggered
        # GPIO.output(self.CLOSING_PIN, False)
        pass
