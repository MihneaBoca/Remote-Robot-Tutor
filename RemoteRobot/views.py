from django.shortcuts import render
import textx
import random

from RemoteRobot.models import Code
from textx import metamodel_from_str
import socket


# initialX = 10
# initialY = 10

def index(request):
    enter_code = "//Enter your code here..."
    output_terminal = ""

    if request.method == 'POST':
        if Code.objects.filter(password=request.POST['password']).exists():
            Code.objects.filter(password=request.POST['password']).delete()
        code = request.POST['terminal']
        password = request.POST['password']

        if password == '':
            message = 'You must provide a robot passcode'
            return render(request, 'index.html',
                          {'code': code, 'password': password, 'message': message})

        new_code = Code.objects.get_or_create(code=code, password=password)[0]
        print(code)
        message = 'Done.'

        grammar = '''

        Program:
            commands*=Command
        ;

        Command:
            ForwardCommand | BackwardCommand | TurnRightCommand | TurnLeftCommand | RepeatCommand | EndRepeatCommand
        ;

        ForwardCommand:
            'Forward' f=FLOAT | 'forward' f=FLOAT | 'F' f=FLOAT | 'f' f=FLOAT
        ;

        BackwardCommand:
            'Backward' b=FLOAT | 'backward' b=FLOAT | 'B' b=FLOAT | 'b' b=FLOAT
        ;

        TurnRightCommand:
            'TurnRight' r=FLOAT |'turnright' r=FLOAT | 'Turn Right' r=FLOAT | 'turn right' r=FLOAT | 'Right' r=FLOAT | 'right' r=FLOAT | 'R' r=FLOAT | 'r' r=FLOAT
        ;

        TurnLeftCommand:
            'TurnLeft' l=FLOAT |'turnleft' l=FLOAT | 'Turn Left' l=FLOAT | 'turn left' l=FLOAT | 'Left' l=FLOAT | 'left' l=FLOAT | 'L' l=FLOAT | 'l' l=FLOAT
        ;
        
        RepeatCommand:
            'Repeat' w=INT | 'repeat' w=INT | 'W' w=INT | 'w' w=INT
        ;
        
        EndRepeatCommand:
            'End' e=STRING? | 'end' e=STRING? | 'E' e=STRING? | 'e' e=STRING?
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

                    elif c.__class__.__name__ == "RepeatCommand":
                        result += 'w ' + str(int(c.w)) + '\n'

                    elif c.__class__.__name__ == "EndRepeatCommand":
                        result += 'e \n'

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
            result = '/'

        count_w = 0
        count_e = 0

        for i in result:
            if i == 'w':
                count_w += 1
            if i == 'e':
                count_e += 1
        if count_w != count_e:
            message = 'The number of Repeat and End needs to be the same'
            return render(request, 'index.html',
                          {'code': code, 'password': password, 'message': message})
        #print(result)
        if count_w != 0:
            result_list = result.splitlines()
            #print('result_list')
            #print(result_list)
            while count_w > 0:
                w = len(result_list)-1
                while not result_list[w].__contains__('w'):
                    w -= 1
                #print(result_list[w])
                e = w
                while not result_list[e].__contains__('e'):
                    e += 1
                #print(result_list[e])
                repeats = int(result_list[w][2:])
                #print(repeats)
                commands = result_list[w+1:e]
                #print(commands)
                repeated_commands = []
                while repeats > 0:
                    #print(commands)
                    for i in commands:
                        repeated_commands.append(i)
                    repeats -= 1
                result_list = result_list[:w] + repeated_commands + result_list[e+1:]
                count_w -= 1
            result = ""
            for i in result_list:
                result += i + '\n'
        #print("result")
        #print(result)

        # return render(request, 'index.html',
        #               {'code': code, 'password': password, 'message': message})


        HOST = '46.101.78.94'  # The server's hostname or IP address
        PORT = 8010  # The port used by the server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(60)
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
    red_size = 3

    coord = [10, 78, 146, 214, 282, 350]

    #print(request.session.keys())

    # del request.session['initialA']
    # del request.session['initialX']
    # del request.session['initialY']
    # del request.session['yellowX']
    # del request.session['yellowY']

    #print(len(coord) - coord.index(int(10)))

    for key in request.session.keys():
        print(request.session[key])

    if 'initialX' in request.session.keys():
        initialX = request.session["initialX"]
    else:
        request.session['initialX'] = coord[random.randrange(len(coord))]
        initialX = request.session["initialX"]

    if 'initialY' in request.session.keys():
        initialY = request.session["initialY"]
    else:
        request.session['initialY'] = coord[random.randrange(len(coord))]
        initialY = request.session["initialY"]

    if 'yellowX' in request.session.keys():
        yellowX = request.session["yellowX"]
    else:
        if coord.index(int(initialX)) < len(coord) / 2:
            # request.session['yellowX'] = coord[len(coord)-coord.index(int(initialX))-1]
            request.session['yellowX'] = coord[len(coord) - 1]
        else:
            request.session['yellowX'] = coord[0]
        yellowX = request.session["yellowX"]

    if 'yellowY' in request.session.keys():
        yellowY = request.session["yellowY"]
    else:
        # request.session['yellowY'] = coord[len(coord)-coord.index(int(initialY))-1]
        # yellowY = request.session["yellowY"]
        if coord.index(int(initialY)) < len(coord) / 2:
            request.session['yellowY'] = coord[len(coord) - 1]
        else:
            request.session['yellowY'] = coord[0]
        yellowY = request.session["yellowY"]

    if 'red_x' in request.session.keys():
        red_x = request.session["red_x"]
    else:
        red_x = []
        for i in range(red_size):
            red_x.append(coord[random.randrange(len(coord))])
        request.session["red_x"] = red_x

    if 'red_y' in request.session.keys():
        red_y = request.session["red_y"]
    else:
        red_y = []
        for i in range(red_size):
            repeat = True
            while repeat:
                repeat = False
                new_red = coord[random.randrange(len(coord))]
                if red_x[i] == initialX:
                    while new_red == initialY:
                        new_red = coord[random.randrange(len(coord))]
                        if red_x[i] == yellowX:
                            while new_red == yellowY:
                                new_red = coord[random.randrange(len(coord))]
                if red_x[i] == yellowX:
                    while new_red == yellowY:
                        new_red = coord[random.randrange(len(coord))]
                        if red_x[i] == initialX:
                            while new_red == initialY:
                                new_red = coord[random.randrange(len(coord))]
                for j in range(len(red_y)):
                    if i != j:
                        if red_x[i] == red_x[j]:
                            if red_y[j] == new_red:
                                repeat = True
            red_y.append(new_red)
        request.session["red_y"] = red_y

    #print(request.session.keys())

    #print(red_x)
    #print(red_y)

    #print(coord.index(int(initialX)) < len(coord) / 2)

    if request.method == 'POST':

        # for i in request.POST:
        #     print(i)

        if 'new_map' in request.POST:
            red_size = int(request.POST['red_squares'])

            initialX = coord[random.randrange(len(coord))]
            request.session['initialX'] = initialX
            # initialX = request.session["initialX"]

            initialY = coord[random.randrange(len(coord))]
            request.session['initialY'] = initialY
            # initialY = request.session["initialY"]

            if coord.index(int(initialX)) < len(coord) / 2:
                request.session['yellowX'] = coord[len(coord) - 1]
            else:
                request.session['yellowX'] = coord[0]
            yellowX = request.session["yellowX"]

            if coord.index(int(initialY)) < len(coord) / 2:
                request.session['yellowY'] = coord[len(coord) - 1]
            else:
                request.session['yellowY'] = coord[0]
            yellowY = request.session["yellowY"]

            red_x = []
            for i in range(red_size):
                red_x.append(coord[random.randrange(len(coord))])
            request.session["red_x"] = red_x

            red_y = []
            for i in range(red_size):
                repeat = True
                while repeat:
                    repeat = False
                    new_red = coord[random.randrange(len(coord))]
                    if red_x[i] == initialX:
                        while new_red == initialY:
                            new_red = coord[random.randrange(len(coord))]
                            if red_x[i] == yellowX:
                                while new_red == yellowY:
                                    new_red = coord[random.randrange(len(coord))]
                    if red_x[i] == yellowX:
                        while new_red == yellowY:
                            new_red = coord[random.randrange(len(coord))]
                            if red_x[i] == initialX:
                                while new_red == initialY:
                                    new_red = coord[random.randrange(len(coord))]
                    for j in range(len(red_y)):
                        if i != j:
                            if red_x[i] == red_x[j]:
                                if red_y[j] == new_red:
                                    repeat = True
                red_y.append(new_red)
            request.session["red_y"] = red_y

            return render(request, 'simulator.html',
                          {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                           'initialX': initialX, 'initialY': initialY, 'yellowX': yellowX, 'yellowY': yellowY,
                           'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

        code = request.POST['terminal']
        print(code)
        message = 'Done.'

        # initialX = request.session['initialX']
        # if initialX is None:
        #     request.session['initialX'] = random.randrange(len(coord))
        # initialX = request.session['initialX']
        # print(initialX)

        grammar = '''

        Program:
            commands*=Command
        ;

        Command:
            ForwardCommand | BackwardCommand | TurnRightCommand | TurnLeftCommand | RepeatCommand | EndRepeatCommand
        ;

        ForwardCommand:
            'Forward' f=STRING? | 'forward' f=STRING? | 'F' f=STRING? | 'f' f=STRING?
        ;

        BackwardCommand:
            'Backward' b=STRING? | 'backward' b=STRING? | 'B' b=STRING? | 'b' b=STRING?
        ;

        TurnRightCommand:
            'TurnRight' r=STRING? |'turnright' r=STRING? | 'Turn Right' r=STRING? | 'turn right' r=STRING? | 'Right' r=STRING? | 'right' r=STRING? | 'R' r=STRING? | 'r' r=STRING?
        ;

        TurnLeftCommand:
            'TurnLeft' l=STRING? |'turnleft' l=STRING? | 'Turn Left' l=STRING? | 'turn left' l=STRING? | 'Left' l=STRING? | 'left' l=STRING? | 'L' l=STRING? | 'l' l=STRING?
        ;
        
        RepeatCommand:
            'Repeat' w=INT | 'repeat' w=INT | 'W' w=INT | 'w' w=INT
        ;
        
        EndRepeatCommand:
            'End' e=STRING? | 'end' e=STRING? | 'E' e=STRING? | 'e' e=STRING?
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
                          {'code': code, 'message': message, 'initialX': initialX, 'initialY': initialY,
                           'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y,
                           'red_size': red_size})

        class Robottutor(object):

            def interpret(self, model):

                # initialise string
                result = ''

                # model is an instance of program
                for c in model.commands:

                    if c.__class__.__name__ == "ForwardCommand":
                        result += 'f'
                        # result += "my_vehicle.drive_straight(" + str(0.2*float(c.f)) + ")" + "\n"#"Forward " + str(c.f)
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "BackwardCommand":
                        result += 'b'
                        # result += "my_vehicle.drive_straight(" + str(-0.2*float(c.b)) + ")" + "\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnRightCommand":
                        result += 'r'
                        # result += "my_vehicle.drive_turn(" + str(float(c.r)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "TurnLeftCommand":
                        result += 'l'
                        # result += "my_vehicle.drive_turn(" + str(-float(c.l)) + ", 0.0)\n"
                        # resultStr = resultStr + result + "\n"

                    elif c.__class__.__name__ == "RepeatCommand":
                        result += 'w' + str(int(c.w))

                    elif c.__class__.__name__ == "EndRepeatCommand":
                        result += 'e'

                    else:
                        print("Invalid")
                return result

        try:
            robot = Robottutor()
            result = robot.interpret(robot_code)
            print(result)
        except AttributeError:
            result = ''

        count_w = 0
        count_e = 0

        for i in result:
            if i == 'w':
                count_w += 1
            if i == 'e':
                count_e += 1
        if count_w != count_e:
            message = 'The number of Repeat and End needs to be the same'
            return render(request, 'simulator.html',
                          {'code': code, 'message': message, 'initialX': initialX, 'initialY': initialY,
                           'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y,
                           'red_size': red_size})

        #print(count_w)
        while count_w != 0:
            w = result.rfind('w')
            e = w
            while result[e] != 'e':
                e += 1
            number = ''
            i = w+1
            #print(result[i])
            while result[i].isdigit():
                number += result[i]
                i += 1
            #print(number)
            commands = result[i:e]
            #print(commands)
            repeats = int(number)
            repeated_commands = ""
            while repeats > 0:
                #print(commands)
                repeated_commands += commands
                repeats -= 1
            #print(commands)
            result = result[:w] + repeated_commands + result[e+1:]
            count_w -= 1

        return render(request, 'simulator.html',
                      {'code': code, 'message': message, 'result': result, 'initialX': initialX, 'initialY': initialY,
                       'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

    return render(request, 'simulator.html',
                  {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                   'initialX': initialX, 'initialY': initialY, 'yellowX': yellowX, 'yellowY': yellowY,
                   'red_x': red_x, 'red_y': red_y, 'red_size': red_size})
