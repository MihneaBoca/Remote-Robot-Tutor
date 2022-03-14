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
        if Code.objects.filter(password=request.POST['password']).exists():
            Code.objects.filter(password=request.POST['password']).delete()
        code = request.POST['terminal']
        password = request.POST['password']
        new_code = Code.objects.get_or_create(code=code, password=password)[0]
        print(code)
        message = 'Done.'

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
                          {'code': code, 'password': password, 'message': message})

        class Robottutor(object):

            def interpret(self, model):

                # initialise string
                result = ''

                # model is an instance of program
                for c in model.commands:

                    if c.__class__.__name__ == "ForwardCommand":
                        result += 'f ' + str(float(c.f)) + '\n'
                        # result += "my_vehicle.drive_straight(" + str(0.2*float(c.f)) + ")" + "\n"#"Forward " + str(c.f)
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "BackwardCommand":
                        result += 'b ' + str(float(c.b)) + '\n'
                        # result += "my_vehicle.drive_straight(" + str(-0.2*float(c.b)) + ")" + "\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnRightCommand":
                        result += 'r ' + str(float(c.r)) + '\n'
                        # result += "my_vehicle.drive_turn(" + str(float(c.r)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnLeftCommand":
                        result += 'l ' + str(float(c.l)) + '\n'
                        # result += "my_vehicle.drive_turn(" + str(-float(c.l)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    else:
                        print("Invalid")
                return result

        try:
            robot = Robottutor()
            result = robot.interpret(robot_code)
            print(result)
            print(password)
        except AttributeError:
            result = ''

        if result == '':
            result = 'Comment'

        HOST = '46.101.78.94'  # The server's hostname or IP address
        PORT = 8010  # The port used by the server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(30)
                s.connect((HOST, PORT))
                data = s.recv(1024)

                print('Received', repr(data))

                my_str_as_bytes = str.encode("website\n" + password)
                # s.sendall(my_str_as_bytes)
                # my_str_as_bytes = str.encode(password)
                s.sendall(my_str_as_bytes)
                data = s.recv(1024)
                print('Received', repr(data))
                message = data.decode("utf-8")
                if message.__contains__('No robot found for the code provided'):
                    s.close()
                    return render(request, 'index.html',
                                  {'code': code, 'password': password, 'message': message})
                my_str_as_bytes = str.encode(result)
                s.sendall(my_str_as_bytes)

            except:
                try:
                    s.close()
                except:
                    pass
                message = 'Connection timeout'
                return render(request, 'index.html',
                              {'code': code, 'password': password, 'message': message})
            s.close()
            return render(request, 'index.html',
                          {'code': code, 'password': password, 'message': message})

    return render(request, 'index.html', {'enter_code': enter_code, 'output_terminal': output_terminal})


def simulator(request):
    enter_code = "//Enter your code here..."
    output_terminal = ""
    result = ""

    if request.method == 'POST':
        code = request.POST['terminal']
        print(code)
        message = 'Done.'

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
            return render(request, 'simulator.html',
                          {'code': code, 'message': message})

        class Robottutor(object):

            def interpret(self, model):

                # initialise string
                result = ''

                # model is an instance of program
                for c in model.commands:

                    if c.__class__.__name__ == "ForwardCommand":
                        result += 'f ' + str(float(c.f)) + ' '
                        # result += "my_vehicle.drive_straight(" + str(0.2*float(c.f)) + ")" + "\n"#"Forward " + str(c.f)
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "BackwardCommand":
                        result += 'b ' + str(float(c.b)) + ' '
                        # result += "my_vehicle.drive_straight(" + str(-0.2*float(c.b)) + ")" + "\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnRightCommand":
                        result += 'r ' + str(float(c.r)) + ' '
                        # result += "my_vehicle.drive_turn(" + str(float(c.r)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnLeftCommand":
                        result += 'l ' + str(float(c.l)) + ' '
                        # result += "my_vehicle.drive_turn(" + str(-float(c.l)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    else:
                        print("Invalid")
                return result

        try:
            robot = Robottutor()
            result = robot.interpret(robot_code)
            print(result)
        except AttributeError:
            result = ''

        return render(request, 'simulator.html',
                      {'code': code, 'message': message, 'result': result})

    return render(request, 'simulator.html',
                  {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result})
