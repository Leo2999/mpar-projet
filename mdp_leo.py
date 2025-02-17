from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from graphviz import Digraph
from models import TemporaryModel

        
class gramPrintListener(gramListener):

    def __init__(self, model):
        self.model = model

    def enterDefstates(self, ctx):
        self.model.states = [str(x) for x in ctx.ID()]
        print("States: %s" % str(self.model.states))

    def enterDefactions(self, ctx):
        self.model.actions = str([str(x) for x in ctx.ID()])
        print("Actions: %s" % str(self.model.actions))

    def enterTransact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]

        for i in range(len(ids)):
            self.model.action_transitions.append({'from': dep, 'action': act, 'to': ids[i], 'weight': weights[i]})

        print("Transition from %s with action %s and targets %s with weights %s" % (dep, act, ids, weights))

    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]

        for i in range(len(ids)):
            self.model.transitions.append({'from': dep, 'to': ids[i], 'weight': weights[i]})

        print("Transition from %s with no action and targets %s with weights %s" % (dep, ids, weights))   

class MarkovGraph:
    def __init__(self, model):
        self.model = model
    
    def plot(self):
        f = Digraph('Markov', filename='Markov.gv')
        f.attr(rankdir='M', size='8,5')
        
        f.attr('node', shape='circle')
        for state in self.model.states:
            f.node(state)
        
        for transition in self.model.transitions:
            f.edge(transition['from'], transition['to'], label=str(transition['weight']))
    
        f.view()

def main():
    lexer = gramLexer(StdinStream())
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    temp_model = TemporaryModel()
    printer = gramPrintListener(temp_model)
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

    model = temp_model.generate_model()

    markov_graph = MarkovGraph(model)
    markov_graph.plot()

    model.simulation_init()
    for _ in range(10):
        model.simulation_step()

if __name__ == '__main__':
    main()

