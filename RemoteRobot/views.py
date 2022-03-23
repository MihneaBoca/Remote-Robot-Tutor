from django.shortcuts import render
import textx
import random

from RemoteRobot.models import Code
from textx import metamodel_from_str
import socket
from collections import deque


class Graph:
    def __init__(self, adj):
        self.adj = adj

    def get_neighbors(self, v):
        return self.adj[v]

    def heuristic(self, n, adj):
        heuristic = {}
        for value in adj:
            heuristic[value] = 1

        return heuristic[n]

    def a_star(self, start, dest, adj):
        not_visited = set([start])
        visited = set([])

        distance = {}
        adj_map = {}

        distance[start] = 0
        adj_map[start] = start

        while len(not_visited) > 0:
            node = None

            for i in not_visited:
                if node is None or distance[i] + self.heuristic(i, adj) < distance[node] + self.heuristic(node, adj):
                    node = i

            if node is None:
                return 'No path to destination'

            if node == dest:
                path = []

                while adj_map[node] != node:
                    path.append(node)
                    node = adj_map[node]

                path.append(start)

                path.reverse()

                return path

            for (i, weight) in self.get_neighbors(node):

                if i not in not_visited and i not in visited:
                    not_visited.add(i)
                    adj_map[i] = node
                    distance[i] = distance[node] + weight

                else:
                    if distance[i] > distance[node] + weight:
                        distance[i] = distance[node] + weight
                        adj_map[i] = node

                        if i in visited:
                            visited.remove(i)
                            not_visited.add(i)

            not_visited.remove(node)
            visited.add(node)

        return 'No path to destination'


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
        if count_w != 0:
            result_list = result.splitlines()
            while count_w > 0:
                w = len(result_list) - 1
                while not result_list[w].__contains__('w'):
                    w -= 1
                e = w
                while not result_list[e].__contains__('e'):
                    e += 1
                repeats = int(result_list[w][2:])
                commands = result_list[w + 1:e]
                repeated_commands = []
                while repeats > 0:
                    for i in commands:
                        repeated_commands.append(i)
                    repeats -= 1
                result_list = result_list[:w] + repeated_commands + result_list[e + 1:]
                count_w -= 1
            result = ""
            for i in result_list:
                result += i + '\n'

        if 'undo' in request.POST:
            result = 'undo'

        if 'disconnect' in request.POST:
            result = 'disconnect'

        HOST = '46.101.78.94'  # The server's hostname or IP address
        PORT = 8010  # The port used by the server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(60)
                s.connect((HOST, PORT))
                data = s.recv(1024)

                my_str_as_bytes = str.encode("website\n" + password)
                s.sendall(my_str_as_bytes)
                data = s.recv(1024)
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
            if result == 'disconnect':
                message += '\nRobot was disconnected'
            return render(request, 'index.html',
                          {'code': code, 'password': password, 'message': message})

    return render(request, 'index.html', {'enter_code': enter_code, 'output_terminal': output_terminal})


def simulator(request):
    enter_code = "//Enter your code here..."
    output_terminal = ""
    result = ""
    red_size = 3

    coord = [10, 78, 146, 214, 282, 350]

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
        no_path = True

        while no_path:
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

            nodes = []

            for i in range(len(coord)):
                for j in range(len(coord)):
                    nodes.append((i, j))

            for i in range(len(red_x)):
                nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

            start = (coord.index(initialX), coord.index(initialY))
            dest = (coord.index(yellowX), coord.index(yellowY))

            adj_list = {}
            for i in range(6):
                for j in range(6):
                    if (i, j) in nodes:
                        neighbours = []
                        if (i + 1, j) in nodes:
                            neighbours.append(((i + 1, j), 1))
                        if (i, j + 1) in nodes:
                            neighbours.append(((i, j + 1), 1))
                        if (i - 1, j) in nodes:
                            neighbours.append(((i - 1, j), 1))
                        if (i, j - 1) in nodes:
                            neighbours.append(((i, j - 1), 1))
                        adj_list[(i, j)] = neighbours

            graph = Graph(adj_list)
            output = graph.a_star(start, dest, nodes)
            if str(output) != 'No path to destination':
                no_path = False

    if request.method == 'POST':

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

            no_path = True

            while no_path:

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

                nodes = []

                for i in range(len(coord)):
                    for j in range(len(coord)):
                        nodes.append((i, j))

                for i in range(len(red_x)):
                    nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

                start = (coord.index(initialX), coord.index(initialY))
                dest = (coord.index(yellowX), coord.index(yellowY))

                adj_list = {}
                for i in range(6):
                    for j in range(6):
                        if (i, j) in nodes:
                            neighbours = []
                            if (i + 1, j) in nodes:
                                neighbours.append(((i + 1, j), 1))
                            if (i, j + 1) in nodes:
                                neighbours.append(((i, j + 1), 1))
                            if (i - 1, j) in nodes:
                                neighbours.append(((i - 1, j), 1))
                            if (i, j - 1) in nodes:
                                neighbours.append(((i, j - 1), 1))
                            adj_list[(i, j)] = neighbours

                graph = Graph(adj_list)
                output = graph.a_star(start, dest, nodes)
                if str(output) != 'No path to destination':
                    no_path = False

            return render(request, 'simulator.html',
                          {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                           'initialX': initialX, 'initialY': initialY, 'yellowX': yellowX, 'yellowY': yellowY,
                           'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

        code = request.POST['terminal']
        message = 'Done.'

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

        while count_w != 0:
            w = result.rfind('w')
            e = w
            while result[e] != 'e':
                e += 1
            number = ''
            i = w + 1
            while result[i].isdigit():
                number += result[i]
                i += 1
            commands = result[i:e]
            repeats = int(number)
            repeated_commands = ""
            while repeats > 0:
                repeated_commands += commands
                repeats -= 1
            result = result[:w] + repeated_commands + result[e + 1:]
            count_w -= 1

        return render(request, 'simulator.html',
                      {'code': code, 'message': message, 'result': result, 'initialX': initialX, 'initialY': initialY,
                       'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

    return render(request, 'simulator.html',
                  {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                   'initialX': initialX, 'initialY': initialY, 'yellowX': yellowX, 'yellowY': yellowY,
                   'red_x': red_x, 'red_y': red_y, 'red_size': red_size})


def short(request):
    enter_code = "//Enter your code here..."
    output_terminal = ""
    result = ""
    red_size = 3
    short_path = 0
    path = 0

    coord = [10, 78, 146, 214, 282, 350]

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
        no_path = True

        while no_path:
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

            nodes = []

            for i in range(len(coord)):
                for j in range(len(coord)):
                    nodes.append((i, j))

            for i in range(len(red_x)):
                nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

            start = (coord.index(initialX), coord.index(initialY))
            dest = (coord.index(yellowX), coord.index(yellowY))

            adj_list = {}
            for i in range(6):
                for j in range(6):
                    if (i, j) in nodes:
                        neighbours = []
                        if (i + 1, j) in nodes:
                            neighbours.append(((i + 1, j), 1))
                        if (i, j + 1) in nodes:
                            neighbours.append(((i, j + 1), 1))
                        if (i - 1, j) in nodes:
                            neighbours.append(((i - 1, j), 1))
                        if (i, j - 1) in nodes:
                            neighbours.append(((i, j - 1), 1))
                        adj_list[(i, j)] = neighbours

            graph = Graph(adj_list)
            output = graph.a_star(start, dest, nodes)
            if str(output) != 'No path to destination':
                no_path = False

    if request.method == 'POST':

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

            no_path = True

            while no_path:

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

                nodes = []

                for i in range(len(coord)):
                    for j in range(len(coord)):
                        nodes.append((i, j))

                for i in range(len(red_x)):
                    nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

                start = (coord.index(initialX), coord.index(initialY))
                dest = (coord.index(yellowX), coord.index(yellowY))

                adj_list = {}
                for i in range(6):
                    for j in range(6):
                        if (i, j) in nodes:
                            neighbours = []
                            if (i + 1, j) in nodes:
                                neighbours.append(((i + 1, j), 1))
                            if (i, j + 1) in nodes:
                                neighbours.append(((i, j + 1), 1))
                            if (i - 1, j) in nodes:
                                neighbours.append(((i - 1, j), 1))
                            if (i, j - 1) in nodes:
                                neighbours.append(((i, j - 1), 1))
                            adj_list[(i, j)] = neighbours

                graph = Graph(adj_list)
                output = graph.a_star(start, dest, nodes)
                if str(output) != 'No path to destination':
                    no_path = False

            return render(request, 'short.html',
                          {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                           'initialX': initialX, 'initialY': initialY, 'yellowX': yellowX, 'yellowY': yellowY,
                           'red_x': red_x, 'red_y': red_y, 'red_size': red_size, 'short_path': short_path,
                           'path': path})

        code = request.POST['terminal']
        message = 'Done.'

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
            robot_code = robot_grammar.model_from_str(code)

        except (textx.exceptions.TextXSyntaxError, AttributeError):
            message = 'Expected comment or Forward, Backward, TurnRight or TurnLeft commands.'
            return render(request, 'short.html',
                          {'code': code, 'message': message, 'initialX': initialX, 'initialY': initialY,
                           'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y,
                           'red_size': red_size, 'short_path': short_path, 'path': path})

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
            return render(request, 'short.html',
                          {'code': code, 'message': message, 'initialX': initialX, 'initialY': initialY,
                           'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y,
                           'red_size': red_size, 'short_path': short_path, 'path': path})

        while count_w != 0:
            w = result.rfind('w')
            e = w
            while result[e] != 'e':
                e += 1
            number = ''
            i = w + 1
            while result[i].isdigit():
                number += result[i]
                i += 1
            commands = result[i:e]
            repeats = int(number)
            repeated_commands = ""
            while repeats > 0:
                repeated_commands += commands
                repeats -= 1
            result = result[:w] + repeated_commands + result[e + 1:]
            count_w -= 1

        nodes = []

        for i in range(len(coord)):
            for j in range(len(coord)):
                nodes.append((i, j))

        for i in range(len(red_x)):
            nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

        start = (coord.index(initialX), coord.index(initialY))
        dest = (coord.index(yellowX), coord.index(yellowY))

        adj_list = {}
        for i in range(6):
            for j in range(6):
                neighbours = []
                if (i + 1, j) in nodes:
                    neighbours.append(((i + 1, j), 1))
                if (i, j + 1) in nodes:
                    neighbours.append(((i, j + 1), 1))
                if (i - 1, j) in nodes:
                    neighbours.append(((i - 1, j), 1))
                if (i, j - 1) in nodes:
                    neighbours.append(((i, j - 1), 1))
                adj_list[(i, j)] = neighbours

        graph = Graph(adj_list)
        output = graph.a_star(start, dest, nodes)
        short_path = len(output) - 1

        for i in result:
            if i == 'f' or i == 'b':
                path += 1

        return render(request, 'short.html',
                      {'code': code, 'message': message, 'result': result, 'initialX': initialX, 'initialY': initialY,
                       'yellowX': yellowX, 'yellowY': yellowY, 'red_x': red_x, 'red_y': red_y, 'red_size': red_size,
                       'short_path': short_path, 'path': path})

    return render(request, 'short.html',
                  {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                   'initialX': initialX, 'initialY': initialY, 'yellowX': yellowX, 'yellowY': yellowY,
                   'red_x': red_x, 'red_y': red_y, 'red_size': red_size, 'short_path': short_path, 'path': path})


def traverse(request):
    enter_code = "//Enter your code here..."
    output_terminal = ""
    result = ""
    red_size = 3

    coord = [10, 78, 146, 214, 282, 350]

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
        no_path = True

        while no_path:
            no_path = False
            red_y = []
            for i in range(red_size):
                repeat = True
                while repeat:
                    repeat = False
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

            nodes = []

            for i in range(len(coord)):
                for j in range(len(coord)):
                    nodes.append((i, j))

            for i in range(len(red_x)):
                nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

            adj_list = {}
            for i in range(6):
                for j in range(6):
                    if (i, j) in nodes:
                        neighbours = []
                        if (i + 1, j) in nodes:
                            neighbours.append(((i + 1, j), 1))
                        if (i, j + 1) in nodes:
                            neighbours.append(((i, j + 1), 1))
                        if (i - 1, j) in nodes:
                            neighbours.append(((i - 1, j), 1))
                        if (i, j - 1) in nodes:
                            neighbours.append(((i, j - 1), 1))
                        adj_list[(i, j)] = neighbours

            graph = Graph(adj_list)
            node = 1
            while node < len(nodes):
                output = graph.a_star(nodes[0], nodes[node], nodes)
                node += 1
                if str(output) == 'No path to destination':
                    no_path = True
                    break

    if request.method == 'POST':

        if 'new_map' in request.POST:
            red_size = int(request.POST['red_squares'])

            initialX = coord[random.randrange(len(coord))]
            request.session['initialX'] = initialX
            # initialX = request.session["initialX"]

            initialY = coord[random.randrange(len(coord))]
            request.session['initialY'] = initialY

            no_path = True

            while no_path:
                no_path = False
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
                        for j in range(len(red_y)):
                            if i != j:
                                if red_x[i] == red_x[j]:
                                    if red_y[j] == new_red:
                                        repeat = True
                    red_y.append(new_red)
                request.session["red_y"] = red_y

                nodes = []

                for i in range(len(coord)):
                    for j in range(len(coord)):
                        nodes.append((i, j))

                for i in range(len(red_x)):
                    nodes.remove((coord.index(red_x[i]), coord.index(red_y[i])))

                adj_list = {}
                for i in range(6):
                    for j in range(6):
                        if (i, j) in nodes:
                            neighbours = []
                            if (i + 1, j) in nodes:
                                neighbours.append(((i + 1, j), 1))
                            if (i, j + 1) in nodes:
                                neighbours.append(((i, j + 1), 1))
                            if (i - 1, j) in nodes:
                                neighbours.append(((i - 1, j), 1))
                            if (i, j - 1) in nodes:
                                neighbours.append(((i, j - 1), 1))
                            adj_list[(i, j)] = neighbours

                graph = Graph(adj_list)
                node = 1
                while node < len(nodes):
                    output = graph.a_star(nodes[0], nodes[node], nodes)
                    node += 1
                    if str(output) == 'No path to destination':
                        no_path = True
                        break

            return render(request, 'traverse.html',
                          {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                           'initialX': initialX, 'initialY': initialY, 'red_x': red_x, 'red_y': red_y,
                           'red_size': red_size})

        code = request.POST['terminal']
        message = 'Done.'

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
            robot_code = robot_grammar.model_from_str(code)

        except (textx.exceptions.TextXSyntaxError, AttributeError):
            message = 'Expected comment or Forward, Backward, TurnRight or TurnLeft commands.'
            return render(request, 'traverse.html',
                          {'code': code, 'message': message, 'initialX': initialX, 'initialY': initialY,
                           'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

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
            return render(request, 'traverse.html',
                          {'code': code, 'message': message, 'initialX': initialX, 'initialY': initialY,
                           'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

        while count_w != 0:
            w = result.rfind('w')
            e = w
            while result[e] != 'e':
                e += 1
            number = ''
            i = w + 1
            while result[i].isdigit():
                number += result[i]
                i += 1
            commands = result[i:e]
            repeats = int(number)
            repeated_commands = ""
            while repeats > 0:
                repeated_commands += commands
                repeats -= 1
            result = result[:w] + repeated_commands + result[e + 1:]
            count_w -= 1

        return render(request, 'traverse.html',
                      {'code': code, 'message': message, 'result': result, 'initialX': initialX, 'initialY': initialY,
                       'red_x': red_x, 'red_y': red_y, 'red_size': red_size})

    return render(request, 'traverse.html',
                  {'enter_code': enter_code, 'output_terminal': output_terminal, 'result': result,
                   'initialX': initialX, 'initialY': initialY, 'red_x': red_x, 'red_y': red_y, 'red_size': red_size})
