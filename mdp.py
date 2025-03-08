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

    def plot_complete_graph(self, highlight_intermediate=None, highlight_node=None, 
                            highlight_edge=None, highlight_next_state=None):

        self.fp = Digraph('MarkovPath', filename='MarkovPath')
        self.fp.attr(rankdir='LR', size='8,5')

        self.fp.attr('node', shape='circle')
        for state in self.model.states:
            fillcolor = 'yellow' if state == highlight_node else 'white'
            self.fp.node(state, style='filled', fillcolor=fillcolor)

        for t in self.model.transitions:
            edge_color = 'black'
            if highlight_edge and (t['from'] == highlight_edge[0]) and (t['to'] == highlight_edge[1]):
                edge_color = 'red'
            label_str = f"({t['weight']})"
            self.fp.edge(t['from'], t['to'], label=label_str, color=edge_color, fontcolor=edge_color)

        if hasattr(self.model, 'action_transitions') and self.model.action_transitions:
            action_groups = {}
            for t in self.model.action_transitions:
                key = (t['from'], t['action'])
                if key not in action_groups:
                    action_groups[key] = []
                action_groups[key].append(t)

            for (from_state, action), transitions in action_groups.items():
                intermediate_node = f"{from_state}_{action}"

                node_color = 'red' if highlight_intermediate == intermediate_node else 'black'
                self.fp.node(intermediate_node, shape='point', width='0.1', color=node_color)

                self.fp.edge(from_state, intermediate_node, label=action, arrowhead='none', color=node_color, fontcolor=node_color)

                for t in transitions:
                    edge_color = 'black'
                    if (highlight_intermediate == intermediate_node) and (highlight_next_state == t['to']):
                        edge_color = 'red'

                    weight_str = f"({t['weight']})"
                    self.fp.edge(intermediate_node, t['to'], label=weight_str, color=edge_color, fontcolor=edge_color)

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
        if len(self.model.path) == 1:
            initial_state = self.model.path[0]
            self.plot_complete_graph(highlight_node=initial_state)
            return
        
        current_state = str(self.model.actual_state)
        previous_state = self.model.path[-2] if len(self.model.path) > 1 else None

        if hasattr(self.model, 'action_transitions') and self.model.action_transitions:
            action = getattr(self.model, 'last_action', None)
            next_state = getattr(self.model, 'last_next_state', None)
            
            highlight_intermediate = None
            highlight_next_state = None
            
            if previous_state and action is not None and next_state is not None:
                highlight_intermediate = f"{previous_state}_{action}"
                highlight_next_state = next_state

            highlight_edge = None
            if action is None and previous_state:
                highlight_edge = (previous_state, current_state)

            self.plot_complete_graph(
                highlight_intermediate=highlight_intermediate,
                highlight_node=current_state,
                highlight_edge=highlight_edge,
                highlight_next_state=highlight_next_state
            )
        else:
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
    if temp_model.verify_model() == 'MDP':
        model.__class__ = MarkovDecisionProcess

    model.build_transition_matrix()

    markov_graph = MarkovGraph(model)
    markov_graph.plot_complete_graph()

    if hasattr(model, 'action_transitions') and model.action_transitions:
        actions = model.simulation_init()
    else:
        model.simulation_init()

    markov_graph.plot_simulation()   
    time.sleep(1) 
    
    if hasattr(model, 'action_transitions') and model.action_transitions:
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
        for _ in range(10):
            model.simulation_step()
            markov_graph.plot_simulation()
            time.sleep(1)

if __name__ == '__main__':
    main()
