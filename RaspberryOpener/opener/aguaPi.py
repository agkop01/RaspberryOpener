from bluetooth import *
import bluetooth, subprocess


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

while True:
    print("Waiting for connection on RFCOMM channel %d" % port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        while True:
            data = client_sock.recv(1024)
            # if len(data) == 0:
            #     break

            print("received [%s]" % data)

            if data[0:6] == 'login=':
                dataArr = data[6:].split('&pass=')
                # if len(dataArr) == 2 and len(dataArr[0]) > 0 and len(dataArr[1]) > 0:
                #
                    # Check if user with given password exists in database (for dataArr[0] as login, dataArr[1] as password)

            elif data[0:7] == 'endConn':
                break


            # if data == 'openGate':
            #     #GPIO.output(17, False)
            #     data = 'openingGate'
            # elif data == 'closeGate':
            #     #GPIO.output(17, True)
            #     data = 'closingGate'
            # else:
            #     data = 'wrongInput'
            # client_sock.send(data)
            # print("sending [%s]" % data)

    except IOError:
        pass

    except KeyboardInterrupt:

        print("disconnected")

        client_sock.close()
        server_sock.close()
        print("all done")

        break

