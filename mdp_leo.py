from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from graphviz import Digraph



class MarkovChain:
    def __init__(self):
        self.states = []
        self.transitions = []

class MarkovDecisionProcess(MarkovChain):
    def __init__(self):
        super().__init__()
        self.actions = []
        self.transitions_with_actions = []
        
class gramPrintListener(gramListener):

    def __init__(self, model):
        self.model = model

    def enterDefstates(self, ctx):
        self.model.states = [str(x) for x in ctx.ID()]
        print("States: %s" % str(self.states))

    def enterDefactions(self, ctx):
        self.model.actions = str([str(x) for x in ctx.ID()])
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

    g = Digraph('Markov', filename='markov.gv')
    g.attr(ranksep="1.5", nodesep="1.0", overlap="false", constraint="false")
    
    for trans in printer.transnoact:
        for i, end in enumerate(trans['to']):
            g.edge(trans['from'], end, label=str(trans['weights'][i]))

    for trans in printer.transact:
        for i, end in enumerate(trans['to']):
            g.edge(trans['from'], end, label=f'{trans['action']}({str(trans['weights'][i])})')

    g.view()

if __name__ == '__main__':
    main()

