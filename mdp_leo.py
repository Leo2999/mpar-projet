from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import sys
from graphviz import Digraph
from models import TemporaryModel
from models import MarkovChain

        
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
    
    def plot_with_path(self):
        
        f = Digraph('MarkovPath', filename='MarkovPath.gv')
        f.attr(rankdir='LR', size='8,5')

        f.attr('node', shape='circle')
        for state in self.model.states:
            f.node(state)

        for transition in self.model.transitions:
            if (transition['from'], transition['to']) in self.path_edges:
                f.edge(transition['from'], transition['to'], label=str(transition['weight']), color="red", penwidth="2.5")
            else:
                f.edge(transition['from'], transition['to'], label=str(transition['weight']), color="black")

        f.view()

    def simulate_and_track(self, steps):

        self.model.simulation_init()
        for _ in range(steps):
            previous_state = self.model.actual_state
            next_state = self.model.simulation_step()
            self.path_edges.append((previous_state, next_state))  
            print(f'{previous_state} -> {next_state}')  


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

    markov_graph.simulate_and_track()    
    markov_graph.plot_with_path()

if __name__ == '__main__':
    main()

