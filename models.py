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

    # verify if all the transitions leaving a state are declared in the same line
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
        self.path = []


    def build_transition_matrix(self):
        self.transition_matrix = []

        for _ in range(len(self.states)):
            matrix_line = []
            for _ in range(len(self.states)):
                matrix_line.append(0)
            self.transition_matrix.append(matrix_line)

        for state in self.states:
            possible_states, probabilities = self.allowed_transitions(state)

            for possible_state, prob in zip(possible_states, probabilities):
                self.transition_matrix[self.states.index(state)][self.states.index(possible_state)] = prob


    def simulation_init(self):
        self.actual_state = self.states[0]
        self.path = [self.actual_state]

        print(f'>>> Simulation initialized: initial state: {self.actual_state}')

    def simulation_step(self):
        possible_states, probabilities = self.allowed_transitions(self.actual_state)

        self.print_allowed_transitions(possible_states, probabilities)

        next_state = np.random.choice(possible_states, p=probabilities)

        print(f'>>> Transition chosen: {self.actual_state}->{next_state}')

        self.actual_state = next_state
        self.path.append(self.actual_state)

        return self.actual_state


    def verif_next(self, from_state, next_state):
        possible_states, probabilities = self.allowed_transitions(from_state)

        print(f'{possible_states=}')
        print(f'{probabilities=}')

        next_prob = 0
        for state, prob in zip(possible_states, probabilities):
            if state == next_state:
                next_prob += prob

        return prob
    
    def verif_until(self, dest_state):
        A = []
        b = []
        for i in range(len(self.transition_matrix)):
            A_line = []
            if self.states[i] != dest_state:
                for j in range(len(self.transition_matrix[0])):
                    if self.states[j] != dest_state:
                        A_line.append(self.transition_matrix[i][j])
                    else:
                        b.append(self.transition_matrix[i][j])
                A.append(A_line)

        for i in range(len(A)):
            print(A[i])

        print(b)

        A = np.array(A)
        b = np.array(b)


        y = np.linalg.solve(np.identity(A.shape[0]) - A, b)
        return y

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

    def simulation_init(self):
        super().simulation_init()
        next_actions = self.verify_actions(self.actual_state)
        return next_actions

    def allowed_transitions(self, state, action=None):
        if action is None:
            return super().allowed_transitions(state)
        else:
            possible_states = []
            probabilities = []
            for transition in self.action_transitions:
                if transition['from'] == state and transition['action'] == action:
                    possible_states.append(transition['to'])
                    probabilities.append(transition['weight'])
            probabilities = np.array(probabilities)
            probabilities = probabilities / np.sum(probabilities)
            return possible_states, probabilities

    def simulation_step(self, action):
        if action is None:
            possible_states, probabilities = super().allowed_transitions(self.actual_state)
            self.print_allowed_transitions(possible_states, probabilities)
            next_state = np.random.choice(possible_states, p=probabilities)
            print(f'>>> Transition chosen: {self.actual_state}->{next_state}\n')
            self.actual_state = next_state
            self.path.append(self.actual_state)
            next_actions = self.verify_actions(self.actual_state)
            # In questo ramo last_action rimane invariato (o potrebbe essere impostato a None)
            return self.actual_state, next_actions
        else:
            print(f'>>> Action performed: {action}')
            self.last_action = action  # IMPOSTA CORRETTAMENTE last_action
            possible_states, probabilities = self.allowed_transitions(self.actual_state, action)
            self.print_allowed_transitions(possible_states, probabilities)
            next_state = np.random.choice(possible_states, p=probabilities)
            print(f'>>> Transition chosen: {self.actual_state}->{next_state}\n')
            self.actual_state = next_state
            self.path.append(self.actual_state)
            next_actions = self.verify_actions(self.actual_state)
            return self.actual_state, next_actions

    def verify_actions(self, state):
        possible_actions = set()
        for transition in self.action_transitions:
            if transition['from'] == state:
                possible_actions.add(transition['action'])

        return possible_actions
