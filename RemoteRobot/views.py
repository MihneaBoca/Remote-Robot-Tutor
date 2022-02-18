import usb
from django.shortcuts import render
from django.contrib import messages
import textx

from RemoteRobot.models import Code
from textx import metamodel_from_str
import ev3_dc as ev3
import socket


def index(request):
    enter_code = "//Enter your code here..."
    output_terminal = ""

    if request.method == 'POST':
        if Code.objects.filter(mac_address=request.POST['mac_address']).exists():
            Code.objects.filter(mac_address=request.POST['mac_address']).delete()
        code = request.POST['terminal']
        mac_address = request.POST['mac_address']
        connection_type = request.POST['connection_type']
        #error_terminal = request.POST['error_terminal']  # request.POST.get('error_terminal', '')#request.POST['error_terminal']
        new_code = Code.objects.get_or_create(code=code, mac_address=mac_address, connection_type=connection_type)[0]
        print(code)
        message = 'Done.'
        PORT = 8010

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(60)
            s.bind(('', PORT))
            s.listen()
            print('Server is waiting...')

            try:
                conn, addr = s.accept()
            except socket.timeout:
                message = 'Connection timeout'
                return render(request, 'index.html',
                              {'code': code, 'mac_address': mac_address, 'connection_type': connection_type,
                               'message': message})
            print('Connected by', addr)
            message = 'Connected by ' + str(addr)
            my_str_as_bytes = str.encode("hello")
            conn.sendall(my_str_as_bytes)
            conn.close()
            return render(request, 'index.html',
                          {'code': code, 'mac_address': mac_address, 'connection_type': connection_type,
                           'message': message})

        grammar = '''

        Program:
            commands*=Command
        ;

        Command:
            ForwardCommand | BackwardCommand | TurnRightCommand | TurnLeftCommand
        ;

        ForwardCommand:
            'Forward' f=FLOAT
        ;

        BackwardCommand:
            'Backward' b=FLOAT
        ;

        TurnRightCommand:
            'TurnRight' r=FLOAT
        ;

        TurnLeftCommand:
            'TurnLeft' l=FLOAT
        ;

        Comment:
            /\/\/.*$/
        ;
        '''
        try:
            robot_grammar = metamodel_from_str(grammar)
            print(robot_grammar)
            robot_code = robot_grammar.model_from_str(code)

        except (textx.exceptions.TextXSyntaxError, AttributeError):
            message = 'Expected comment or Forward, Backward, TurnRight or TurnLeft commands.'
            return render(request, 'index.html',
                          {'code': code, 'mac_address': mac_address, 'connection_type': connection_type,
                           'message': message})

        class Robottutor(object):

            def interpret(self, model):

                # initialise string
                result = []

                # model is an instance of program
                for c in model.commands:

                    if c.__class__.__name__ == "ForwardCommand":
                        result.append('f ' + str(0.2 * float(c.f)))
                        # result += "my_vehicle.drive_straight(" + str(0.2*float(c.f)) + ")" + "\n"#"Forward " + str(c.f)
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "BackwardCommand":
                        result.append('b ' + str(-0.2 * float(c.b)))
                        # result += "my_vehicle.drive_straight(" + str(-0.2*float(c.b)) + ")" + "\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnRightCommand":
                        result.append('r ' + str(-float(c.r)))
                        # result += "my_vehicle.drive_turn(" + str(float(c.r)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnLeftCommand":
                        result.append('l ' + str(float(c.l)))
                        # result += "my_vehicle.drive_turn(" + str(-float(c.l)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    else:
                        print("Invalid")
                return result

        try:
            robot = Robottutor()
            result = robot.interpret(robot_code)
            print(result)
            print(mac_address)
        except AttributeError:
            result = []

        if connection_type == 'usb':
            protocol = ev3.USB
        elif connection_type == 'wifi':
            protocol = ev3.WIFI
        else:
            protocol = ev3.BLUETOOTH

        try:

            with ev3.TwoWheelVehicle(
                    0.01518,  # radius_wheel
                    0.11495,  # tread
                    protocol=protocol,
                    host=str(mac_address),
                    speed=10
            ) as my_vehicle:
                parcours = my_vehicle.drive_straight(0.0)
                for i in result:
                    if i[0] == 'f':
                        my_vehicle.drive_straight(float(i[2:])).start(thread=False)
                    elif i[0] == 'b':
                        my_vehicle.drive_straight(float(i[2:])).start(thread=False)
                    elif i[0] == 'r':
                        my_vehicle.drive_turn(float(i[2:]), 0.0).start(thread=False)
                    elif i[0] == 'l':
                        my_vehicle.drive_turn(float(i[2:]), 0.0).start(thread=False)
        except ev3.exceptions.NoEV3:
            message = "No EV3 found.\n"
            # messages.error(request, "No EV3 found.")
        except usb.core.NoBackendError:
            message = "No backend available for USB.\n"
            # messages.error(request, "No EV3 found.")

            # parcours = (exec(robot.interpret(robot_code)))
            # parcours.start(thread=False)
        return render(request, 'index.html',
                      {'code': code, 'mac_address': mac_address, 'connection_type': connection_type,
                       'message': message})

    return render(request, 'index.html', {'enter_code': enter_code, 'output_terminal': output_terminal})
