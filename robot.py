#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from time import sleep
import ev3dev.fonts as fonts
from ev3dev2.motor import OUTPUT_A, OUTPUT_D, MoveDifferential, SpeedRPM
from ev3dev2.wheel import EV3Tire
import socket

HOST = '46.101.78.94'  # The server's hostname or IP address
PORT = 8010  # The port used by the server


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        data = s.recv(1024)

        #print('Received', repr(data))

        my_str_as_bytes = str.encode("robot")
        s.sendall(my_str_as_bytes)

        data = s.recv(1024)

        #print('Received', repr(data))

        code = s.recv(1024)

        #print('Received', repr(data))

        lcd = ev3.Screen()
        lcd.draw.text((20, 50), code.decode("utf-8"), font=fonts.load('luBS12'))
        lcd.update()
        # sleep(6)

        check = True

        while check:
            my_str_as_bytes = str.encode("alive")
            s.sendall(my_str_as_bytes)
            data = s.recv(1024)
            if data.decode("utf-8").__contains__('Connected to website'):
                lcd = ev3.Screen()
                lcd.draw.text((25, 50), data.decode("utf-8"), font=fonts.load('luBS12'))
                lcd.update()
                sleep(6)
                data = s.recv(1024)
                #print(data.decode("utf-8"))
                if data.decode("utf-8") != '':
                    web_code = data.decode("utf-8").splitlines()
                else:
                    web_code = ['']
                try:
                    mdiff = MoveDifferential(OUTPUT_A, OUTPUT_D, EV3Tire, 16 * 8)
                    for i in web_code:
                        if i[0] == 'f':
                            mdiff.on_for_distance(SpeedRPM(40), float(i[2:])*100)
                        elif i[0] == 'b':
                            mdiff.on_for_distance(SpeedRPM(40), -float(i[2:]) * 100)
                        elif i[0] == 'r':
                            mdiff.turn_right(SpeedRPM(40), float(i[2:]))
                        elif i[0] == 'l':
                            mdiff.turn_left(SpeedRPM(40), float(i[2:]))
                except:
                    check = False
                    s.close()
                    exit()
                lcd = ev3.Screen()
                lcd.draw.text((25, 50), code.decode("utf-8"), font=fonts.load('luBS12'))
                lcd.update()

        s.close()
    finally:
        s.close()