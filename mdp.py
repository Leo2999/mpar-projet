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
        # Salva le azioni come lista
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
        
    def plot_complete_graph(self, highlight_edge=None, highlight_intermediate=None, highlight_node=None):
        # Ricrea il grafo da zero
        self.fp = Digraph('MarkovPath', filename='MarkovPath')
        self.fp.attr(rankdir='LR', size='8,5')
        
        if hasattr(self.model, 'action_transitions') and self.model.action_transitions:
            # Modalità MDP: utilizza nodi intermedi per le transizioni con azione
            self.fp.attr('node', shape='circle')
            for state in self.model.states:
                fill = 'yellow' if state == highlight_node else 'white'
                self.fp.node(state, style='filled', fillcolor=fill)
            
            # Raggruppa le transizioni per coppia (stato di partenza, azione)
            action_groups = {}
            for transition in self.model.action_transitions:
                key = (transition['from'], transition['action'])
                if key not in action_groups:
                    action_groups[key] = []
                action_groups[key].append(transition)
            
            # Per ogni gruppo crea un nodo intermedio e disegna le frecce
            for (from_state, action), transitions in action_groups.items():
                intermediate_node = f"{from_state}_{action}_intermediate"
                edge_color = 'red' if highlight_intermediate == intermediate_node else 'black'
                # Nodo intermedio (lo evidenzia se necessario)
                self.fp.node(intermediate_node, shape='point', width='0.1', color=edge_color)
                # Arco dal nodo di partenza al nodo intermedio con etichetta azione
                self.fp.edge(from_state, intermediate_node, arrowhead='none',
                             label=action, color=edge_color, fontcolor=edge_color)
                # Arco dal nodo intermedio agli stati di destinazione con etichetta peso
                for t in transitions:
                    self.fp.edge(intermediate_node, t['to'], label=str(t['weight']),
                                 color=edge_color, fontcolor=edge_color)
        else:
            # Modalità MC: evidenzia lo stato corrente e, se presente, la transizione corrente (highlight_edge)
            self.fp.attr('node', shape='circle')
            for state in self.model.states:
                fill = 'yellow' if state == highlight_node else 'white'
                self.fp.node(state, style='filled', fillcolor=fill)
            for transition in self.model.transitions:
                # Se l'arco corrisponde a highlight_edge, lo coloriamo di rosso
                edge_color = 'red' if highlight_edge and transition['from'] == highlight_edge[0] and transition['to'] == highlight_edge[1] else 'black'
                self.fp.edge(transition['from'], transition['to'], label=str(transition['weight']),
                             color=edge_color, fontcolor=edge_color)
                
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

        if hasattr(self.model, 'action_transitions') and self.model.action_transitions:
            # Modalità MDP: evidenzia il nodo intermedio relativo alla transizione corrente
            action = getattr(self.model, 'last_action', None)
            highlight_intermediate = None
            if previous_state and action is not None:
                highlight_intermediate = f"{previous_state}_{action}_intermediate"
            self.plot_complete_graph(highlight_intermediate=highlight_intermediate, highlight_node=current_state)
        else:
            # Modalità MC: evidenzia l'arco dalla transizione (stato precedente -> stato corrente)
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

    # Genera il modello; se è MDP, si usa la versione modificata
    model = temp_model.generate_model()
    if temp_model.verify_model() == 'MDP':
        # Sostituisci il modello con la versione modificata per memorizzare last_action
        model.__class__ = MarkovDecisionProcess

    model.build_transition_matrix()

    markov_graph = MarkovGraph(model)
    markov_graph.plot_complete_graph()

    if hasattr(model, 'action_transitions') and model.action_transitions:
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