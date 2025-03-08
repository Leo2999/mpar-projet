import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import time
from gramLexer import gramLexer  # Assicurati che il file 'gramLexer.py' sia presente
from gramParser import gramParser  # Assicurati che il file 'gramParser.py' sia presente
from antlr4 import *
from models import TemporaryModel, MarkovDecisionProcess
from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener

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
        self.G = nx.DiGraph()  # Grafo diretto
        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.plot_complete_graph()

    def plot_complete_graph(self):
        self.G.clear()  # Svuotiamo il grafo

        # Creiamo i nodi per tutti gli stati
        for state in self.model.states:
            self.G.add_node(state)

        # Aggiungiamo le transizioni senza azione
        for transition in self.model.transitions:
            self.G.add_edge(transition['from'], transition['to'], weight=transition['weight'], color='black')

        # Se il modello è un MarkovDecisionProcess, aggiungiamo anche le transizioni con azioni
        if isinstance(self.model, MarkovDecisionProcess):
            for transition in self.model.action_transitions:
                self.G.add_edge(transition['from'], transition['to'], weight=transition['weight'], color='black', action=transition['action'])

        self.update_plot()

    def update_plot(self):
        # Impostiamo le posizioni dei nodi per evitare che si sovrappongano
        pos = nx.spring_layout(self.G)

        # Rimuoviamo gli archi esistenti per renderizzare il nuovo grafo
        edge_colors = [self.G[u][v]['color'] for u, v in self.G.edges()]
        weights = [self.G[u][v]['weight'] for u, v in self.G.edges()]

        # Disegniamo i nodi e gli archi
        nx.draw(self.G, pos, with_labels=True, node_size=5000, node_color='skyblue', font_size=10, font_weight='bold', ax=self.ax, edge_color=edge_colors, width=2)
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels={(u, v): f"{d['weight']}" for u, v, d in self.G.edges(data=True)}, ax=self.ax)

        # Visualizziamo il grafico
        self.ax.axis('off')
        plt.draw()
        plt.pause(1)

    def plot_simulation(self):
        current_state = str(self.model.actual_state)

        if len(self.model.path) > 1:
            previous_state = self.model.path[-2]
        else:
            previous_state = None

        # Ripristiniamo il grafo completo
        self.plot_complete_graph()

        # Evidenziamo lo stato corrente
        self.G.nodes[current_state]['color'] = 'yellow'

        # Se esiste una transizione precedente, la aggiungiamo
        if self.current_edge:
            self.G[self.current_edge[0]][self.current_edge[1]]['color'] = 'black'
            self.current_edge = None

        # Aggiungiamo solo l'ultima transizione in rosso
        if previous_state:
            transition_found = False
            for transition in self.model.transitions:
                if transition['from'] == previous_state and transition['to'] == current_state:
                    # Rimuoviamo la freccia nera
                    if self.G.has_edge(transition['from'], transition['to']):
                        self.G[transition['from']][transition['to']]['color'] = 'white'  # Rimuoviamo l'arco disegnandolo bianco

                    # Ora aggiungiamo la transizione rossa
                    self.G.add_edge(previous_state, current_state, weight=transition['weight'], color='red')
                    self.current_edge = (previous_state, current_state)
                    transition_found = True
                    break

            # Se non è stata trovata una transizione tra previous_state e current_state, non tracciarla
            if not transition_found:
                print(f"Nessuna transizione trovata tra {previous_state} e {current_state}.")

        # Rende di nuovo il grafico
        self.update_plot()

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
