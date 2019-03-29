def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def format_colours(S, colours):
    fgcolour    = colours["fg"]
    bgcolour    = colours["bg"]
    lightcolour = colours["light"]
    darkcolour  = colours["dark"]
    return S.format(fg=fgcolour, bg=bgcolour, dark=darkcolour, light=lightcolour)

def read_multiline(s):
    out = {}
    current_key = ""
    current_string = ""
    pos = 0
    s = s.split("\n")
    s_copy = s[:]
    s = []
    for i in s_copy:
        if not i == "":
            s.append(i)
    
    while not pos > len(s) - 1:
        current_key = s[pos]
        pos += 1
        while s[pos] == "" or s[pos].isspace():
            pos += 1

        if not s[pos].strip(" \n\t") == '"""':
            raise SyntaxError("Expected '\"\"\"' before '{s}'".format(s=s[pos]))

        pos += 1
        while not s[pos].strip(" \n\t") == '"""':
            try:
                current_string += s[pos] + "\n"
                pos += 1
            except IndexError:
                raise SyntaxError("Unexpected EOF while parsing")

        pos += 1
        out[current_key] = current_string[:-1]
        current_string = ""
    return out
        
def create_multiline(d):
    out = ""
    for key in d:
        out += key + "\n"
        out += '"""' + "\n"
        out += d[key] + "\n"
        out += '"""' + "\n"
    return out
