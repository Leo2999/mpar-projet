import numpy as np

class TemporaryModel:
    def __init__(self):
        self.states = []
        self.actions = []
        self.transitions = []
        self.action_transitions = []
        self.model_type = None

    # verify if some state doesn't have a leaving transition
    # if so, add a 100% transition to itself
    def verify_model(self):
        self.model_type = 'MDP' if len(self.action_transitions) > 0 else 'MC'

        for transition in self.transitions:
            if transition['from'] not in self.states:
                raise Exception(f'Error: undeclared state: {transition["from"]}') 
            if transition['to'] not in self.states:
                raise Exception(f'Error: undeclared state: {transition["to"]}')
            
        if self.model_type == 'MDP':
            for transition in self.action_transitions:
                if transition["action"] not in self.actions:
                    raise Exception(f'Error: undeclared action: {transition["action"]}')
                
            action_states = set()
            for transition in self.action_transitions:
                action_states.add(transition["from"])
            
            for transition in self.transitions:
                if transition['from'] in action_states:
                    raise Exception(f'Error: transitions with and without actions leaving state {transition["from"]}')
                
        return self.model_type
            

    def generate_model(self):
        if self.verify_model() == 'MC':
            return MarkovChain(self.states, self.transitions)
        else:
            return MarkovDecisionProcess(
                self.states,
                self.actions,
                self.transitions,
                self.action_transitions
            )

class MarkovChain:
    def __init__(self, states, transitions, simulation_trace=True):
        self.states = states
        self.transitions = transitions
        self.simulation_trace = simulation_trace
        self.path = []

    def simulation_init(self):
        self.actual_state = self.states[0]
        self.path = [self.actual_state]

        if self.simulation_trace:
            print(f'>>> Simulation initialized: initial state: {self.actual_state}')

    def simulation_step(self):
        possible_states, probabilities = self.allowed_transitions(self.actual_state)

        if self.simulation_trace:
            self.print_allowed_transitions(possible_states, probabilities)

        next_state = np.random.choice(possible_states, p=probabilities)

        if self.simulation_trace:
            print(f'>>> Transition chosen: {self.actual_state}->{next_state}')

        self.actual_state = next_state
        self.path.append(self.actual_state)

        return self.actual_state

    def allowed_transitions(self, state):
        possible_states = []
        probabilities = []
        for transition in self.transitions:
            if transition['from'] == state:
                possible_states.append(transition['to'])
                probabilities.append(transition['weight'])
        
        probabilities = np.array(probabilities)
        probabilities = probabilities / np.sum(probabilities)

        return possible_states, probabilities
    
    def print_allowed_transitions(self, possible_states, probabilities):
        print('>>> Possible Transitions')
        for i in range(len(possible_states)):
            print(f'{self.actual_state}->{possible_states[i]}: {probabilities[i]*100}%')
        print()

class MarkovDecisionProcess(MarkovChain):
    def __init__(self, states, actions, transitions, action_transitions):
        super().__init__(states, transitions)
        self.actions = actions
        self.action_transitions = action_transitions