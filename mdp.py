from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import numpy as np
from graphviz import Digraph
from models import TemporaryModel, MarkovDecisionProcess
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
        self.model.actions = [str(x) for x in ctx.ID()]
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
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.plot_complete_graph()

    def plot_complete_graph(self, highlight_edge=None, highlight_node=None):
        self.fp = Digraph('MarkovPath', filename='MarkovPath')
        self.fp.attr(rankdir='LR', size='8,5')
        self.fp.attr('node', shape='circle')

        for state in self.model.states:
            fill = 'yellow' if state == highlight_node else 'white'
            self.fp.node(state, style='filled', fillcolor=fill)

        for transition in self.model.transitions:
            color = 'red' if highlight_edge and transition['from'] == highlight_edge[0] and transition['to'] == highlight_edge[1] else 'black'
            self.fp.edge(transition['from'], transition['to'], label=str(transition['weight']), color=color)

        if hasattr(self.model, 'action_transitions') and self.model.action_transitions:
            for transition in self.model.action_transitions:
                color = 'red' if highlight_edge and transition['from'] == highlight_edge[0] and transition['to'] == highlight_edge[1] else 'black'
                label = f"{transition['action']} ({transition['weight']})"
                self.fp.edge(transition['from'], transition['to'], label=label, color=color)

        self.fp.render(format='png', cleanup=True)
        self.update_plot()

    def update_plot(self):
        image = mpimg.imread('MarkovPath.png')
        self.ax.clear()
        self.ax.imshow(image)
        self.ax.axis('off')
        plt.draw()
        plt.pause(0.5)

    def plot_simulation(self):
        current_state = str(self.model.actual_state)
        previous_state = self.model.path[-2] if len(self.model.path) > 1 else None

        highlight_edge = (previous_state, current_state) if previous_state else None

        self.plot_complete_graph(highlight_edge=highlight_edge, highlight_node=current_state)


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
    model.build_transition_matrix()

    markov_graph = MarkovGraph(model) 
    markov_graph.plot_complete_graph()

    if isinstance(model, MarkovDecisionProcess):
        actions = model.simulation_init()
        for _ in range(10):
            if len(actions) == 0:
                _, actions = model.simulation_step(None)
                markov_graph.plot_simulation()
                time.sleep(1)
            else:
                action = np.random.choice(list(actions))
                _, actions = model.simulation_step(action)
                markov_graph.plot_simulation()
                time.sleep(1)
    else:
        model.simulation_init()
        for _ in range(10):
            model.simulation_step()
            markov_graph.plot_simulation()
            time.sleep(1)

if __name__ == '__main__':
    main()
