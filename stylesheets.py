from constants import *
from json import loads
from strings import format_colours, read_multiline
#text colours etc. loaded from file
with open("styles.json", "r") as f:
    styles_json = loads(f.read())

with open("stylesheets.json", "r") as f:
    stylesheets = read_multiline(f.read())

styles = styles_json["colours"]
fgcolour    = styles["fg"]
bgcolour    = styles["bg"]
lightcolour = styles["light"]
darkcolour  = styles["dark"]
builtin_colour  = styles["builtin"]
keyword_colour  = styles["keyword"]
operator_colour = styles["operator"]
brace_colour    = styles["brace"]
defclass_colour = styles["defclass"]
string_colour   = styles["string"]
string2_colour  = styles["string2"]
comment_colour  = styles["comment"]
self_colour     = styles["self"]
numbers_colour  = styles["numbers"]

colours = {"fg"   : fgcolour,
           "bg"   : bgcolour,
           "light": lightcolour,
           "dark" : darkcolour}

styles = styles_json["words"]
builtins  = styles["builtins"]
keywords  = styles["keywords"]
operators = styles["operators"]
braces    = styles["braces"]

#styles = styles_json["stylesheets"]
#QTreeViewStyle = styles["QTreeViewStyle"].format(fg=fgcolour, bg=bgcolour, dark=darkcolour, light=lightcolour)

stylesheets = {i:format_colours(stylesheets[i], colours) for i in stylesheets}

QTreeViewStyle       = stylesheets["QTreeViewStyle"]
QTreeViewHeaderStyle = stylesheets["QTreeViewHeaderStyle"]
QVScrollbarStyle     = stylesheets["QVScrollbarStyle"]
QHScrollbarStyle     = stylesheets["QHScrollbarStyle"]
QMainWindowStyle     = stylesheets["QMainWindowStyle"]
QWidgetStyle         = stylesheets["QWidgetStyle"]
QMenuStyle           = stylesheets["QMenuStyle"]
QTabWidgetStyle      = stylesheets["QTabWidgetStyle"]
QPlainTextStyle      = stylesheets["QPlainTextStyle"]

def reload_words():
    with open("styles.json", "r") as f:
        styles_json = loads(f.read()) 
    styles = styles_json["words"]
    builtins  = styles["builtins"]
    keywords  = styles["keywords"]
    operators = styles["operators"]
    braces    = styles["braces"]
