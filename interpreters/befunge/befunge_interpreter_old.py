import sys, random

def matrixise(code):
    matrix = []
    for i, line in enumerate(code.split("\n")):
        matrix.append([])
        for j, char in enumerate(line):
            matrix[i].append(char)

    return matrix

def pad(matrix):
    length = max([len(i) for i in matrix])
    result = []
    for row in matrix:
        if len(row) < length:
            c = row.copy()
            while len(c) < length:
                c.append(" ")
            result.append(c)
        else:
            result.append(row)
    return  result

class Interpreter:
    def __init__(self, code):
        print(code)
        self.m = pad(matrixise(code))
        self.ip = [0, 0]
        self.direction = "right"
        self.error = None
        self.running = True
        self.stringMode = False
        self.stack = []

    def step_debug(self):
        x = [i for i in self.step()]
        return (self.ip[1], self.ip[0])
    
    def step(self):
        curr_char = self.m[self.ip[0]][self.ip[1]]
        #print(curr_char + ", " + str(self.stack))
        if self.stringMode and not curr_char == "\"":
            self.stack.append(ord(curr_char))
        elif curr_char.isdigit():
            self.stack.append(int(curr_char))
        else:
            #directions
            if curr_char == ">":
                self.direction = "right"
            elif curr_char == "<":
                self.direction = "left"
            elif curr_char == "^":
                self.direction = "up"
            elif curr_char == "v":
                self.direction = "down"
            #operations
            elif curr_char == "\"":
                self.stringMode = not self.stringMode
                
            elif curr_char == ",":
                yield chr(self.pop())
                
            elif curr_char == "&":
                num = 0
                inp = sys.stdin.readline()
                try:
                    num = int(inp)
                except ValueError:
                    pass

                self.stack.append(num)
                
            elif curr_char == "-":
                a = self.pop()
                b = self.pop()
                self.stack.append(b - a)

            elif curr_char == "+":
                a = self.pop()
                b = self.pop()
                self.stack.append(a + b)

            elif curr_char == "/":
                a = self.pop()
                b = self.pop()
                self.stack.append(b // a)

            elif curr_char == "*":
                a = self.pop()
                b = self.pop()
                self.stack.append(a * b)

            elif curr_char == "%":
                a = self.pop()
                b = self.pop()
                self.stack.append(a % b)

            elif curr_char == "\\":
                a = self.pop()
                b = self.pop()
                self.stack.append(b)
                self.stack.append(a)

            elif curr_char == "$":
                self.pop()

            elif curr_char == ".":
                yield str(self.pop()) + " "

            elif curr_char == "#":
                self.move_pc()

            elif curr_char == "g":
                try:
                    y = self.pop()
                    x = self.pop()
                    character = self.m[y][x]
                    self.stack.append(ord(character))
                except IndexError:
                    self.stack.append(0)

            elif curr_char == "p":
                y = self.pop()
                x = self.pop()
                v = chr(self.pop())
                try:
                    self.m[y][x] = v
                except IndexError:
                    if y >= len(self.m):
                        while y >= len(self.m):
                            self.m.append([])
                    else:
                        if x >= len(self.m[y]):
                            while x >= len(self.m[y]):
                                self.m[y].append(" ")
                    self.m = pad(self.m)
                    self.m[y][x] = v
                
            elif curr_char == "~":
                inp = input("Enter a character: ")
                while len(inp) != 1:
                    inp = input("Enter a character: ")

                self.stack.append(ord(inp)) ############################################################################################################

            elif curr_char == "!":
                a = self.pop()
                if a == 0:
                    self.stack.append(1)
                else:
                    self.stack.append(0)

            elif curr_char == "`":
                a = self.pop()
                b = self.pop()
                self.stack.append(int(b > a))

            elif curr_char == "?":
                self.direction = ["left", "right", "up", "down"][random.randint(0, 3)]

            elif curr_char == "_":
                value = self.pop()
                if value == 0:
                    self.direction = "right"
                else:
                    self.direction = "left"
                
            elif curr_char == ":":
                value = self.pop()
                self.stack.append(value)
                self.stack.append(value)
                
            elif curr_char == "|":
                value = self.pop()
                if value == 0:
                    self.direction = "down"
                else:
                    self.direction = "up"
                    
            elif curr_char == "@":
                self.running = False
                return
            
        self.move_pc()

    def pop(self):
        try:
            return self.stack.pop()
        except:
            return 0

    def debugprint(self):
        out = ""
        for y, row in enumerate(self.m):
            for x, col in enumerate(row):
                if x == self.ip[1] and y == self.ip[0]:
                    out += '\x1b[6;30;42m' + col + '\x1b[0m'
                else:
                    out += col
            out += "\n"
        print(out)

    def move_pc(self):
        if self.direction == "right":
            self.ip[1] += 1
        elif self.direction == "left":
            self.ip[1] -= 1
        elif self.direction == "up":
            self.ip[0] -= 1
        elif self.direction == "down":
            self.ip[0] += 1

    def run(self):
        while self.running:
            out = self.step()
            if out != None:
                yield out

##i = Interpreter(""""t"44p44g,@""")
##for a in i.run():
##    for thing in a:
##        print(thing)
