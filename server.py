import socket
import random


PORT = 8010

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("remoterobottutor-tp7vf.ondigitalocean.app", 80))
s.close()
robot = {}

words = ("python", "jumble", "easy", "difficult", "answer", "xylophone", "rock", "paper", "scissor", "adventure",
         "plane", "ship", "car", "robot", "school", "dog", "cat", "mouse", "book", "tv", "rocket", "house", "mango",
         "apple", "plum", "bear", "friend", "lion", "jungle", "laser", "question", "lemon", "orange", "green", "red",
         "blue", "yellow", "purple", "brown", "sun", "moon", "paint", "song", "melody", "carpet", "table", "lake",
         "sea", "sand", "castle", "bubble", "zebra", "whale", "napkin", "magic", "egg", "eye", "fish", "ocean", "vase",
         "zoo", "soccer", "sugar", "spoon", "stone", "king", "candle", "kite", "ice", "snow", "rain", "queen", "knight",
         "quill", "honey", "potato", "tomato", "plastic", "pizza", "planet", "horse", "guitar", "piano", "pillow",
         "pencil", "rainbow", "river", "room", "rose", "shoe", "train", "world", "computer", "science", "library",
         "idea", "story", "game", "week", "movie", "film", "truth", "goal", "teacher", "student", "flight", "city",
         "heart", "hotel", "lab", "town", "gate", "pie", "poem", "tea", "bug", "insect", "menu", "ear", "hat", "night",
         "day", "tale", "time", "water", "air", "place", "hand", "point", "card", "mind", "line", "group", "key",
         "name", "level", "lift", "web", "fun", "page", "test", "sound", "focus", "kind", "soil", "board", "picture",
         "future", "garden", "boat", "class", "plan", "space", "earth", "salt", "speed", "bank", "bus", "box", "metal",
         "view", "ball", "gift", "choice", "wind", "hope", "date", "voice", "plant", "summer", "spring", "winter",
         "autumn", "fall", "button", "sky", "fruit", "tree", "gold", "bag", "farm", "nose", "mirror", "camp", "flower",
         "clock", "joke", "ring", "tower", "hello", "remote", "tiger", "bird", "owl", "monkey")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind(('', PORT))
        s.listen()
        print('Server is waiting...')

        while True:
            print(robot)
            remove = []
            for i in list(robot):

                print('checking')
                try:
                    check = robot[i][0].recv(1204)
                    #print(check.decode("utf-8"))
                    if not check.decode("utf-8").__contains__('alive'):
                        remove.append(i)
                    else:
                        robot[i][0].sendall(str.encode("check"))
                except:
                    remove.append(i)
            for i in remove:
                del robot[i]
            #print(robot)
            print('accepting connections')
            conn, addr = s.accept()
            print('Connected by', addr)
            my_str_as_bytes = str.encode("hello")
            conn.sendall(my_str_as_bytes)
            status = conn.recv(1204)
            #print(status.decode("utf-8"))
            if status.decode("utf-8").__contains__('robot'):
                conn.sendall(str.encode("You are a robot"))
                while True:
                    word1 = random.choice(words)
                    word2 = random.choice(words)
                    while word1 == word2:
                        word2 = random.choice(words)
                    word3 = random.choice(words)
                    while word2 == word3:
                        word3 = random.choice(words)
                    code = word1 + '-' + word2 + '-' + word3
                    if code not in robot.keys():
                        break
                robot[code] = (conn, addr)
                conn.sendall(str.encode(code))
                #print("c-")
                # print(robot[code][0].connect_ex(robot[code][1]))

                for i in list(robot):
                    # print(robot[i][0].connect_ex(robot[i][1]))
                    print('checking')
                    try:
                        check = robot[i][0].recv(1204)
                        #print(check.decode("utf-8"))
                        if not check.decode("utf-8").__contains__('alive'):
                            remove.append(i)
                        else:
                            robot[i][0].sendall(str.encode("check"))
                    except:
                        remove.append(i)
                for i in remove:
                    del robot[i]

            if status.decode("utf-8").__contains__('website'):
                robot_code = status.decode("utf-8").splitlines()[1]
                #print(robot_code)
                if robot_code in robot:
                    try:
                        #print(robot[robot_code])
                        robot[robot_code][0].recv(1204)
                        robot[robot_code][0].sendall(str.encode("Connected to website"))
                        conn.sendall(str.encode("Connected to robot"))
                        result = conn.recv(1204)
                        #print(result.decode("utf-8"))
                        robot[robot_code][0].sendall(result)
                    except:
                        pass

                    for i in list(robot):
                        print('checking')
                        try:
                            check = robot[i][0].recv(1204)
                            #print(check.decode("utf-8"))
                            if not check.decode("utf-8").__contains__('alive'):
                                remove.append(i)
                            else:
                                robot[i][0].sendall(str.encode("check"))
                        except:
                            remove.append(i)
                    for i in remove:
                        del robot[i]

                else:
                    conn.sendall(str.encode("No robot found for the code provided"))
    except:
        s.close()
    finally:
        s.close()
