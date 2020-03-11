import sys

from PyQt5.QtCore import QRegExp
from PyQt5 import QtGui
#from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from stylesheets import managerInstance as SSM

def formatStyle(style):
    """Return a QTextCharFormat with the given attributes.
    """
    colour = style[0]
    colour_bg = style[1]
    style = style[2]
    
    _colour = QtGui.QColor()
    _colour.setNamedColor(colour)

    _colour_bg = QtGui.QColor()
    _colour_bg.setNamedColor(colour_bg)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_colour)
    _format.setBackground(_colour_bg)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format

class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)
        # Python keywords
        self.STYLES = {
            'keyword': formatStyle(SSM.keyword_colour),
            'builtins': formatStyle(SSM.builtin_colour),
            'operator': formatStyle(SSM.operator_colour),
            'brace': formatStyle(SSM.brace_colour),
            'defclass': formatStyle(SSM.defclass_colour),
            'string': formatStyle(SSM.string_colour),
            'string2': formatStyle(SSM.string2_colour),
            'comment': formatStyle(SSM.comment_colour),
            'self': formatStyle(SSM.self_colour),
            'numbers': formatStyle(SSM.numbers_colour),
        }
        self.builtins = SSM.builtins
        self.keywords = SSM.keywords

        # Python operators
        self.operators = SSM.operators

        # Python braces
        self.braces = SSM.braces

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("\'\'\'"), 1, self.STYLES['string2'])
        self.tri_double = (QRegExp('\"\"\"'), 2, self.STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, self.STYLES['keyword'])
            for w in self.keywords]
        rules += [(r'\b%s\b' % w, 0, self.STYLES['builtins'])
            for w in self.builtins]
        rules += [(r'%s' % o, 0, self.STYLES['operator'])
            for o in self.operators]
        rules += [(r'%s' % b, 0, self.STYLES['brace'])
            for b in self.braces]

        # All other rules
        rules += [
            (r'\b[+-]?[0-9]+[lL]?\b', 0, self.STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, self.STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, self.STYLES['numbers']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, self.STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, self.STYLES['defclass']),
            
            # 'self'
            (r'\bself\b', 0, self.STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, self.STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, self.STYLES['string']),
                    
            # From '#' until a newline
            (r'#[^\n]*', 0, self.STYLES['comment']),

        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]

    def redefine_words(self):
        #reload_words()
        self.builtins = SSM.builtins
        self.keywords = SSM.keywords
        self.operators = SSM.operators
        self.braces = SSM.braces

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False
