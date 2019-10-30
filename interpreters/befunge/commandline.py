#!/usr/bin/python3
import sys, befunge_interpreter

def usage():
    print("Usage: " + sys.argv[0] + " <filename>")
    sys.exit(1)

if len(sys.argv) < 2:
    usage()

try:
    with open(sys.argv[1], "r") as f:
        code = f.read()
except IOError:
    print("Cannot read file " + sys.argv[1])
    sys.exit(1)

i = befunge_interpreter.Interpreter(code)
for a in i.run():
    b = list(a)
    if len(b) > 0:
        sys.stdout.write("".join(b))
        sys.stdout.flush()
