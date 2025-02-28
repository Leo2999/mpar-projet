from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
from graphviz import Digraph
from models import TemporaryModel
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import time

        
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
        self.visited = set()
        self.edges_drawn = set()
        self.fp = Digraph('MarkovPath', filename='MarkovPath')
        self.fp.attr(rankdir='LR', size='8,5')
        self.fp.attr('node', shape='circle')
        plt.ion() 
        self.fig, self.ax = plt.subplots()

    def plot(self):
        f = Digraph('Markov', filename='Markov.gv')
        f.attr(rankdir='LR', size='8,5')
        f.attr('node', shape='circle')
        
        for state in self.model.states:
            f.node(state)
        
        for transition in self.model.transitions:
            f.edge(transition['from'], transition['to'], label=str(transition['weight']))

        f.render(format='png')
        image = mpimg.imread('Markov.gv.png')
        self.ax.clear()
        self.ax.imshow(image)
        self.ax.axis('off')
        plt.draw()

    def plot_simulation(self):
        current_state = str(self.model.actual_state)

        if len(self.model.path) > 1:
            previous_state = self.model.path[-2] 
        else: 
            None
        
        for state in self.visited:
            self.fp.node(state, style='filled', fillcolor='white')
        
        if previous_state and (previous_state, current_state) not in self.edges_drawn:
            self.fp.edge(previous_state, current_state, color='red')
            self.edges_drawn.add((previous_state, current_state))
        
        self.fp.node(current_state, style='filled', fillcolor='yellow')
        self.visited.add(current_state)
        
        self.fp.render(format='png')
        image = mpimg.imread('MarkovPath.png')
        self.ax.clear()
        self.ax.imshow(image)
        self.ax.axis('off')
        plt.draw()
        plt.pause(1) 

        
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
        markov_graph.plot_simulation()
        time.sleep(1)

if __name__ == '__main__':
    main()

