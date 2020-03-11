from constants import *
from json import loads
from strings import format_colours, read_multiline

class StyleSheetManager:
    def __init__(self):
        self.raw_stylesheets = None
        self.fgcolour    = None
        self.bgcolour    = None
        self.lightcolour = None
        self.darkcolour  = None
        self.builtin_colour  = None
        self.keyword_colour  = None
        self.operator_colour = None
        self.brace_colour    = None
        self.defclass_colour = None
        self.string_colour   = None
        self.string2_colour  = None
        self.comment_colour  = None
        self.self_colour     = None
        self.numbers_colour  = None

        self.builtins  = None
        self.keywords  = None
        self.operators = None
        self.braces    = None

        self.colours = None
        self.stylesheets = None
        self.StyleSheet = None

    def textStyleFormat(self, style):
        return [x.format(bg=self.bgcolour, fg=self.fgcolour, light=self.lightcolour, dark=self.darkcolour) for x in style]

    def saveSheet(sheetName, sheetContents):
        print("NOPE NOT TODAY THANK YOU")
    
    def loadSheets(self):
        with open("styles.json", "r") as f:
            styles_json = loads(f.read())

        with open("stylesheets.json", "r") as f:
            self.raw_stylesheets = read_multiline(f.read())

        styles = styles_json["colours"]
        self.fgcolour    = styles["fg"]
        self.bgcolour    = styles["bg"]
        self.lightcolour = styles["light"]
        self.darkcolour  = styles["dark"]
        self.builtin_colour  = self.textStyleFormat(styles["builtin"])
        self.keyword_colour  = self.textStyleFormat(styles["keyword"])
        self.operator_colour = self.textStyleFormat(styles["operator"])
        self.brace_colour    = self.textStyleFormat(styles["brace"])
        self.defclass_colour = self.textStyleFormat(styles["defclass"])
        self.string_colour   = self.textStyleFormat(styles["string"])
        self.string2_colour  = self.textStyleFormat(styles["string2"])
        self.comment_colour  = self.textStyleFormat(styles["comment"])
        self.self_colour     = self.textStyleFormat(styles["self"])
        self.numbers_colour  = self.textStyleFormat(styles["numbers"])

        self.colours = {"fg"   : self.fgcolour,
                        "bg"   : self.bgcolour,
                        "light": self.lightcolour,
                        "dark" : self.darkcolour}

        styles = styles_json["words"]
        self.builtins  = styles["builtins"]
        self.keywords  = styles["keywords"]
        self.operators = styles["operators"]
        self.braces    = styles["braces"]

        #styles = styles_json["stylesheets"]
        #QTreeViewStyle = styles["QTreeViewStyle"].format(fg=fgcolour, bg=bgcolour, dark=darkcolour, light=lightcolour)

        self.stylesheets = {i:format_colours(self.raw_stylesheets[i], self.colours) for i in self.raw_stylesheets}

        self.StyleSheet = "\n".join([self.stylesheets[i] for i in self.stylesheets])

managerInstance = StyleSheetManager()
