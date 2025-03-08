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
        self.current_edge = None
        self.fp = Digraph('MarkovPath', filename='MarkovPath')
        self.fp.attr(rankdir='LR', size='8,5')
        self.fp.attr('node', shape='circle')
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.plot_complete_graph()

    def plot_complete_graph(self):
        self.fp.clear()
        self.fp.attr(rankdir='LR', size='8,5')
        self.fp.attr('node', shape='circle')

        # Creiamo i nodi per tutti gli stati
        for state in self.model.states:
            self.fp.node(state, style='filled', fillcolor='white')

        # Creiamo le transizioni senza azione
        for transition in self.model.transitions:
            self.fp.edge(transition['from'], transition['to'], label=str(transition['weight']), color='black')

        # Se il modello è un MarkovDecisionProcess, creiamo anche le transizioni con azioni
        if isinstance(self.model, MarkovDecisionProcess):
            for transition in self.model.action_transitions:
                self.fp.edge(transition['from'], transition['to'], label=f"{transition['action']} ({transition['weight']})", color='black')

        # Renderizziamo il grafico
        self.fp.render(format='png')
        self.update_plot()

    def update_plot(self):
        image = mpimg.imread('MarkovPath.png')
        self.ax.clear()
        self.ax.imshow(image)
        self.ax.axis('off')
        plt.draw()
        plt.pause(1)

    def plot_simulation(self):
        current_state = str(self.model.actual_state)

        if len(self.model.path) > 1:
            previous_state = self.model.path[-2]
        else:
            previous_state = None

        self.fp.clear()  # Svuotiamo il grafico corrente
        self.plot_complete_graph()  # Ripristiniamo il grafico di base

        # Evidenziamo lo stato corrente
        self.fp.node(current_state, style='filled', fillcolor='yellow')

        # Se esiste una transizione precedente, la aggiungiamo
        if self.current_edge:
            self.fp.edge(self.current_edge[0], self.current_edge[1], color='black', label=str(self.get_transition_weight(self.current_edge[0], self.current_edge[1])))
            self.current_edge = None

        # Aggiungiamo solo l'ultima transizione in rosso, se esiste
        if previous_state:
            transition_found = False
            for transition in self.model.transitions:
                if transition['from'] == previous_state and transition['to'] == current_state:
                    # Prima rimuoviamo la freccia nera, se esiste
                    self.fp.edge(transition['from'], transition['to'], color='white')  
                    
                    # Ora disegniamo la transizione in rosso
                    self.fp.edge(previous_state, current_state, color='red', label=str(transition['weight']))
                    self.current_edge = (previous_state, current_state)
                    transition_found = True
                    break
            
            # Se non è stata trovata una transizione tra previous_state e current_state, non tracciarla
            if not transition_found:
                print(f"Nessuna transizione trovata tra {previous_state} e {current_state}.")
        
        # Renderizziamo il grafico con la transizione rossa
        self.fp.render(format='png')
        self.update_plot()

    def get_transition_weight(self, from_state, to_state):
        for transition in self.model.transitions:
            if transition['from'] == from_state and transition['to'] == to_state:
                return transition['weight']
        return ''
       
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
