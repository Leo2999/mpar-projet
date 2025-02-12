from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from graphviz import Digraph


        
class gramPrintListener(gramListener):

    def __init__(self):
        self.states = []
        self.actions = []
        self.transact = []
        self.transnoact = []
        
    def enterDefstates(self, ctx):
        self.states = [str(x) for x in ctx.ID()]
        print("States: %s" % str(self.states))

    def enterDefactions(self, ctx):
        self.actions = str([str(x) for x in ctx.ID()])
        print("Actions: %s" % str(self.actions))

    def enterTransact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]

        self.transact.append({"from": dep, "action": act, "to": ids,"weights": weights})

        print("Transition from %s with action %s and targets %s with weights %s" % (dep, act, ids, weights))

    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]

        self.transnoact.append({"from": dep, "to": ids, "weights": weights})

        print("Transition from %s with no action and targets %s with weights %s" % (dep, ids, weights))   

    def plotMarkov(self, ctx):
        pass


def main():
    lexer = gramLexer(StdinStream())
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    printer = gramPrintListener()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

if __name__ == '__main__':
    main()

