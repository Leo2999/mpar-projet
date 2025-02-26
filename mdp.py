from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import numpy as np
from graphviz import Digraph
from models import TemporaryModel, MarkovChain, MarkovDecisionProcess

        
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

    def plot_simulation(self):
        f = Digraph('MarkovPath', filename='MarkovPath.gv')
        f.attr(rankdir='LR', size='8,5')

        f.attr('node', shape='circle')

        visited_states = set(self.model.path) 
        for state in visited_states:
            f.node(state)

        path_edges = set()

        for i in range(len(self.model.path) - 1):
            from_state = self.model.path[i]
            to_state = self.model.path[i + 1]
            path_edges.add((from_state, to_state)) 

        for transition in self.model.transitions:
            from_state = transition['from']
            to_state = transition['to']
            edge = (from_state, to_state)

            if edge in path_edges:
                f.edge(from_state, to_state, color="red", penwidth="2.5")
            else:
                f.edge(from_state, to_state, color="black")

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

    if type(model) == MarkovChain:
        model.simulation_init()
        for _ in range(10):
            model.simulation_step()
    else:
        actions = model.simulation_init()
        for _ in range(10):
            if len(actions) == 0:
                _, actions = model.simulation_step(None)
            else:
                action = np.random.choice(list(actions))
                _, actions = model.simulation_step(action)
        

if __name__ == '__main__':
    main()

