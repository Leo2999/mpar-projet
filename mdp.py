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
import sys

class gramPrintListener(gramListener):
    def __init__(self, model):
        self.model = model

    def enterDefstates(self, ctx):
        self.model.states = [str(x) for x in ctx.ID()]

    def enterDefactions(self, ctx):
        self.model.actions = [str(x) for x in ctx.ID()]

    def enterTransact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        for i in range(len(ids)):
            self.model.action_transitions.append({
                'from': dep,
                'action': act,
                'to': ids[i],
                'weight': weights[i]
            })

    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]
        for i in range(len(ids)):
            self.model.transitions.append({'from': dep,'to': ids[i],'weight': weights[i]})

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

    def plot_complete_graph(self, highlight_intermediate=None, highlight_node=None, highlight_edge=None, highlight_next_state=None):
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
                if t['action'] == "no_action":
                    continue
                key = (t['from'], t['action'])
                if key not in action_groups:
                    action_groups[key] = []
                action_groups[key].append(t)
            for (from_state, action), transitions in action_groups.items():
                intermediate_node = f"{from_state}_{action}"
                node_color = 'red' if highlight_intermediate == intermediate_node else 'black'
                self.fp.node(intermediate_node, shape='point', width='0.1', color=node_color)
                self.fp.edge(from_state, intermediate_node,
                            label=action, arrowhead='none',
                            color=node_color, fontcolor=node_color)
                for t in transitions:
                    edge_color = 'black'
                    if (highlight_intermediate == intermediate_node) and (highlight_next_state == t['to']):
                        edge_color = 'red'
                    weight_str = f"({t['weight']})"
                    self.fp.edge(intermediate_node, t['to'],
                                label=weight_str, color=edge_color, fontcolor=edge_color)

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
            
            if previous_state and action == "no_action" and next_state is not None:
                highlight_edge = (previous_state, current_state)
                highlight_intermediate = None
                highlight_next_state = None
            
            elif previous_state and action is not None and next_state is not None:
                highlight_intermediate = f"{previous_state}_{action}"
                highlight_next_state = next_state
                highlight_edge = None
            else:
                highlight_intermediate = None
                highlight_next_state = None
                highlight_edge = None

            self.plot_complete_graph(
                highlight_intermediate=highlight_intermediate,
                highlight_node=current_state,
                highlight_edge=highlight_edge,
                highlight_next_state=highlight_next_state
            )
        else:
            highlight_edge = (previous_state, current_state) if previous_state else None
            self.plot_complete_graph(
                highlight_edge=highlight_edge,
                highlight_node=current_state
            )

def main():
    filename = sys.argv[1]
    lexer = gramLexer(FileStream(filename))
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    temp_model = TemporaryModel()
    printer = gramPrintListener(temp_model)
    walker = ParseTreeWalker()
    walker.walk(printer, tree)
    model = temp_model.generate_model()
    print("""Options: 
            1 - Simulate the model
            2 - Verify the properties
          """)
    choice = int(input('What do you want to do? '))
    if choice == 1:
        print('>>> Simulating model')
        steps = int(input('How many steps do you want to simulate? '))
        markov_graph = MarkovGraph(model)
        markov_graph.plot_complete_graph()
        if isinstance(model, MarkovDecisionProcess):
            actions = model.simulation_init()
            markov_graph.plot_simulation()  
            time.sleep(1)
            for _ in range(steps):
                action = np.random.choice(list(actions))
                _, actions = model.simulation_step(action)
                markov_graph.plot_simulation()
                time.sleep(1)
        else:
            model.simulation_init()
            markov_graph.plot_simulation()
            time.sleep(1)
            for _ in range(steps):
                model.simulation_step()
                markov_graph.plot_simulation()
                time.sleep(1)
    elif choice == 2:
        property = input('Which properties do you want to verify? ')
        print(""" Techniques:
                1 - Linear system resolution
                2 - Iterative resolution
                3 - SMC resolution
              """)
        technique = int(input('Which technique do you want to use? '))
        if technique == 1:
            y = model.verify_property_linear_system(property)
            print(f'Probability: {y}')
        elif technique == 2:
            print('Not implemented')
        if technique == 3:
            gama = model.verify_property_smc(property, 0.01, 0.01)
            print(f'Probability: {gama}')
    else:
        print('>>> Error in the choice')

if __name__ == '__main__':
    main()