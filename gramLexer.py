# Generated from gram.g4 by ANTLR 4.13.2
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,12,74,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,1,0,1,0,1,0,1,
        0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,3,1,3,1,
        3,1,4,1,4,1,5,1,5,1,6,1,6,1,7,1,7,1,8,1,8,1,9,4,9,57,8,9,11,9,12,
        9,58,1,10,1,10,5,10,63,8,10,10,10,12,10,66,9,10,1,11,4,11,69,8,11,
        11,11,12,11,70,1,11,1,11,0,0,12,1,1,3,2,5,3,7,4,9,5,11,6,13,7,15,
        8,17,9,19,10,21,11,23,12,1,0,4,1,0,48,57,3,0,65,90,95,95,97,122,
        4,0,48,57,65,90,95,95,97,122,3,0,9,10,12,13,32,32,76,0,1,1,0,0,0,
        0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,0,13,
        1,0,0,0,0,15,1,0,0,0,0,17,1,0,0,0,0,19,1,0,0,0,0,21,1,0,0,0,0,23,
        1,0,0,0,1,25,1,0,0,0,3,32,1,0,0,0,5,40,1,0,0,0,7,42,1,0,0,0,9,45,
        1,0,0,0,11,47,1,0,0,0,13,49,1,0,0,0,15,51,1,0,0,0,17,53,1,0,0,0,
        19,56,1,0,0,0,21,60,1,0,0,0,23,68,1,0,0,0,25,26,5,83,0,0,26,27,5,
        116,0,0,27,28,5,97,0,0,28,29,5,116,0,0,29,30,5,101,0,0,30,31,5,115,
        0,0,31,2,1,0,0,0,32,33,5,65,0,0,33,34,5,99,0,0,34,35,5,116,0,0,35,
        36,5,105,0,0,36,37,5,111,0,0,37,38,5,110,0,0,38,39,5,115,0,0,39,
        4,1,0,0,0,40,41,5,58,0,0,41,6,1,0,0,0,42,43,5,45,0,0,43,44,5,62,
        0,0,44,8,1,0,0,0,45,46,5,59,0,0,46,10,1,0,0,0,47,48,5,44,0,0,48,
        12,1,0,0,0,49,50,5,43,0,0,50,14,1,0,0,0,51,52,5,91,0,0,52,16,1,0,
        0,0,53,54,5,93,0,0,54,18,1,0,0,0,55,57,7,0,0,0,56,55,1,0,0,0,57,
        58,1,0,0,0,58,56,1,0,0,0,58,59,1,0,0,0,59,20,1,0,0,0,60,64,7,1,0,
        0,61,63,7,2,0,0,62,61,1,0,0,0,63,66,1,0,0,0,64,62,1,0,0,0,64,65,
        1,0,0,0,65,22,1,0,0,0,66,64,1,0,0,0,67,69,7,3,0,0,68,67,1,0,0,0,
        69,70,1,0,0,0,70,68,1,0,0,0,70,71,1,0,0,0,71,72,1,0,0,0,72,73,6,
        11,0,0,73,24,1,0,0,0,4,0,58,64,70,1,6,0,0
    ]

class gramLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    STATES = 1
    ACTIONS = 2
    DPOINT = 3
    FLECHE = 4
    SEMI = 5
    VIRG = 6
    PLUS = 7
    LCROCH = 8
    RCROCH = 9
    INT = 10
    ID = 11
    WS = 12

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'States'", "'Actions'", "':'", "'->'", "';'", "','", "'+'", 
            "'['", "']'" ]

    symbolicNames = [ "<INVALID>",
            "STATES", "ACTIONS", "DPOINT", "FLECHE", "SEMI", "VIRG", "PLUS", 
            "LCROCH", "RCROCH", "INT", "ID", "WS" ]

    ruleNames = [ "STATES", "ACTIONS", "DPOINT", "FLECHE", "SEMI", "VIRG", 
                  "PLUS", "LCROCH", "RCROCH", "INT", "ID", "WS" ]

    grammarFileName = "gram.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


