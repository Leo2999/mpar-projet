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
            self.model.transitions_with_actions.append({'from': dep, 'action': act, 'to': ids[i], 'weight': weights[i]})

        print("Transition from %s with action %s and targets %s with weights %s" % (dep, act, ids, weights))

    def enterTransnoact(self, ctx):
        ids = [str(x) for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(str(x)) for x in ctx.INT()]

        for i in range(len(ids)):
            self.model.transitions.append({'from': dep, 'to': ids[i], 'weight': weights[i]})

        print("Transition from %s with no action and targets %s with weights %s" % (dep, ids, weights))   

'''
class MarkovGraph:
    def __init__(self, model):
        self.model = model
    
    def plot(self):
        f = Digraph('Markov', filename='Markov.gv')
        f.attr(rankdir='M', size='8,5')
        
        f.attr('node', shape='circle')
        for state in self.model.states:
            f.node(state)

        for i in range(len(self.model.transitions_with_actions)):
            f.edge(
                self.model.transitions_with_actions[i]["from"],
                self.model.transitions_with_actions[i]["to"],
                label=f'{self.model.transitions_with_actions[i]["action"]} ({self.model.transitions_with_actions[i]["weight"]})'
            )

            #if self.model.transitions_with_actions[i]["actions"] is not None:
             #   f.edge('model.transitions_with_actions[i]["from"]', 'model.transitions_with_actions[i]["to"]')
    
    #creare un nodo intermedio per fare la biforcazione
        
        f.view()

'''
class MarkovGraph:
    def __init__(self, model):
        self.model = model

    def plot(self):
        f = Digraph('Markov', filename='Markov.gv')
        f.attr(rankdir='LR', size='8,5')

        f.attr('node', shape='circle')
        for state in self.model.states:
            f.node(state)

        # Creiamo un dizionario per tracciare gli stati che hanno più azioni possibili
        state_action_map = {}
        for transition in self.model.transitions_with_actions:
            state_action_map.setdefault(transition["from"], []).append(transition)

        for state, transitions in state_action_map.items():
            if len(transitions) > 1:
                # Creiamo un nodo intermedio per la scelta
                decision_node = f"choice_{state}"
                f.node(decision_node, shape='circ', width="0")

                # Collegamento dello stato originale al nodo decisionale
                f.edge(state, decision_node)

                # Collegamento del nodo decisionale alle varie opzioni con azioni e pesi
                for transition in transitions:
                    f.edge(
                        decision_node,
                        transition["to"],
                        label=f'{transition["action"]} ({transition["weight"]})'
                    )
            else:
                # Caso con una sola azione: collegamento diretto
                transition = transitions[0]
                f.edge(
                    transition["from"],
                    transition["to"],
                    label=f'{transition["action"]} ({transition["weight"]})'
                )

        # Aggiungiamo anche le transizioni senza azione
        for transition in self.model.transitions:
            f.edge(
                transition["from"],
                transition["to"],
                label=str(transition["weight"])
            )

        f.render(format='pdf', view=True)    # Genera e visualizza il grafico
     

def main():
    lexer = gramLexer(StdinStream())
    stream = CommonTokenStream(lexer)
    parser = gramParser(stream)
    tree = parser.program()
    model = TemporaryModel()
    printer = gramPrintListener(model)
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

    print(model.states)
    print(model.actions)
    print(model.transitions)
    print(model.transitions_with_actions)

    prova = MarkovGraph(model)
    prova.plot()

if __name__ == '__main__':
    main()

