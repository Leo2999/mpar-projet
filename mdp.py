from antlr4 import *
from gramLexer import gramLexer
from gramListener import gramListener
from gramParser import gramParser
import numpy as np
from graphviz import Digraph
from models import TemporaryModel, MarkovDecisionProcess, MarkovChain
from matplotlib import pyplot as plt    
import matplotlib.image as mpimg
import time
import sys

class gramPrintListener(gramListener):
    def __init__(self, model):
        self.model = model

    def enterDefstates(self, ctx):
        if ctx.state_reward_list() is not None:
            rewards = {}
            for sr in ctx.state_reward_list().state_reward():
                state = sr.ID().getText()  
                reward_val = int(sr.INT().getText()) 
                rewards[state] = reward_val
            self.model.states = list(rewards.keys())
            self.model.state_rewards = rewards
        elif ctx.state_list() is not None:
            id_tokens = ctx.state_list().getTokens(gramParser.ID)
            self.model.states = [token.getText() for token in id_tokens]
            self.model.state_rewards = {}

            
    def enterDefactions(self, ctx):
        self.model.actions = [x.getText() for x in ctx.ID()]

    def enterTransact(self, ctx):
        ids = [x.getText() for x in ctx.ID()]
        dep = ids.pop(0)
        act = ids.pop(0)
        weights = [int(x.getText()) for x in ctx.INT()]
        for i in range(len(ids)):
            self.model.action_transitions.append({
                'from': dep,
                'action': act,
                'to': ids[i],
                'weight': weights[i]
            })

    def enterTransnoact(self, ctx):
        ids = [x.getText() for x in ctx.ID()]
        dep = ids.pop(0)
        weights = [int(x.getText()) for x in ctx.INT()]
        for i in range(len(ids)):
            self.model.transitions.append({
                'from': dep,
                'to': ids[i],
                'weight': weights[i]
            })

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
            3 - Verify the expected reward
            4 - Reinforcement Learning
          """)
    choice = int(input('What do you want to do (1,2,3 or 4)? '))
    while choice not in [1, 2, 3, 4]:
                print("Invalid option. Please choose 1,2 or 3.")
                choice = int(input('What do you want to do (1, 2 or 3)? '))
    if choice == 1:
        print('>>> Simulating model')
        steps = int(input('How many steps do you want to simulate? '))
        markov_graph = MarkovGraph(model)
        markov_graph.plot_complete_graph()
        if isinstance(model, MarkovDecisionProcess):
            print("""Simulation mode options:  
                    1 - Random simulation
                    2 - Manual simulation
                  """)
            sim_mode = input("Choose simulation mode (1 or 2): ")
            while sim_mode not in ['1', '2']:
                print("Invalid option. Please choose 1 or 2.")
                sim_mode = input("Choose simulation mode (1 or 2): ")
            actions = model.simulation_init()
            markov_graph.plot_simulation()
            time.sleep(1)
            for i in range(steps):
                print(f"Step {i+1}:")
                if sim_mode == '1':
                    action = np.random.choice(list(actions))
                    print("Randomly chosen action:", action)
                else:
                    if actions == {"no_action"}:
                        action = "no_action"
                        print("No decision required")
                    else:
                        available_actions = [a for a in actions if a != "no_action"]
                        print("Available actions: " + ", ".join(available_actions))
                        action = input("Choose an action: ")
                        while action not in available_actions:
                            print("Invalid action. Please choose one of the following:")
                            print(", ".join(available_actions))
                            action = input("Choose an action: ")
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
        property = input('Which properties do you want to verify? (indicate the state) ')

        if not isinstance(model, MarkovDecisionProcess):
            print(""" Techniques:
                    1 - Linear system resolution
                    2 - Iterative resolution
                    3 - SMC quantitative resolution
                    4 - SMC qualitative resolution
                """)
            technique = int(input('Which technique do you want to use (1,2, 3, 4 or 5)? '))
            while technique not in [1, 2, 3, 4, 5]:
                    print("Invalid technique. Please choose 1,2, 3, 4 or 5.")
                    technique = int(input('What do you want to do (1,2, 3, 4 or 5)? '))
            if technique == 1:
                y = model.verify_property_linear_system(property)
                print(f'Probability: {y}')
            elif technique == 2:
                initial_state = input('Initial State: ')    
                y = model.verify_property_iterative(property, initial_state)
                print(f'Probability: {y}')
            elif technique == 3:
                gama = model.verify_property_smc_quant(property, 0.01, 0.01)
                print(f'Probability: {gama}')
            elif technique == 4:
                theta = float(input('Theta value? '))
                epsilon = float(input('Epsilon value? '))
                res = model.verify_property_smc_qual(property, theta, epsilon)

                if res == 1:
                    print(f'The probability is smaller than {theta}')
                elif res == 0:
                    print(f'The probability is bigger than {theta}')
                else:
                    print('Answer not found')
        else:
            y = model.verify_property_linear(property)
            print(f'Probability: {y}')
    elif choice == 3:
        markov_graph = MarkovGraph(model)
        markov_graph.plot_complete_graph()
        initial_state = input('Initial State:' )
        target_state = input('Target State: ')
        if not isinstance(model, MarkovDecisionProcess):
            expected_reward = model.expected_reward_MC(initial_state, target_state)
            print(f'The expected reward from {initial_state} to {target_state} is: {expected_reward}')
        else:
            expected_reward = model.expected_reward_MDP(initial_state, target_state)
            print(f'The expected reward from {initial_state} to {target_state} is: {expected_reward}')
    elif choice == 4:
        if isinstance(model, MarkovDecisionProcess):
            Q = model.q_learning()
            for i, state in enumerate(model.states):
                for j, action in enumerate(model.actions):
                    print(f'>>> {state}({action}) : {Q[i*len(model.actions) + j]}')

    else:
        print('>>> Error in the choice')

if __name__ == '__main__':
    main()
