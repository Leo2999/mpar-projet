import numpy as np
from copy import deepcopy
from scipy.optimize import linprog

class TemporaryModel:
    def __init__(self):
        self.states = []
        self.actions = []
        self.transitions = []
        self.action_transitions = []
        self.model_type = None

    def verify_model(self):
        self.model_type = 'MDP' if len(self.action_transitions) > 0 else 'MC'

        for transition in self.transitions:
            if transition['from'] not in self.states:
                raise Exception(f'Error: undeclared state: {transition["from"]}')
            if transition['to'] not in self.states:
                raise Exception(f'Error: undeclared state: {transition["to"]}')
            
        if self.model_type == 'MDP':
            for transition in self.action_transitions:
                if transition['from'] not in self.states:
                    raise Exception(f'Error: undeclared state: {transition["from"]}')
                if transition['to'] not in self.states:
                    raise Exception(f'Error: undeclared state: {transition["to"]}')


            for transition in self.action_transitions:
                if transition["action"] not in self.actions:
                    raise Exception(f'Error: undeclared action: {transition["action"]}')
                
            action_states = set()
            for transition in self.action_transitions:
                action_states.add(transition["from"])
            
            for transition in self.transitions:
                if transition['from'] in action_states:
                    raise Exception(f'Error: transitions with and without actions leaving state {transition["from"]}')
            
            for t in self.transitions:
                self.action_transitions.append({'from': t['from'],'to': t['to'],'weight': t['weight'],'action': 'no_action'})
            
            for state in self.states:
                there_is_transition = False
                for t in self.transitions:
                    if t['from'] == state:
                        there_is_transition = True
                        break
                if not there_is_transition and state not in action_states:
                    self.transitions.append({'from': state, 'to': state, 'weight': 1})
        
        else:
            for state in self.states:
                there_is_transition = False
                for t in self.transitions:
                    if t['from'] == state:
                        there_is_transition = True
                        break
                if not there_is_transition:
                    self.transitions.append({'from': state, 'to': state, 'weight': 1})
                
        return self.model_type
            

    def generate_model(self):
        if self.verify_model() == 'MC':
            model = MarkovChain(self.states, self.transitions)
            model.state_rewards = self.state_rewards  
            return model
        
        else:
            model = MarkovDecisionProcess(
                self.states,
                self.actions,
                self.transitions,
                self.action_transitions
            )
            model.state_rewards = self.state_rewards  
            return model

class MarkovChain:
    def __init__(self, states, transitions, simulation_trace=True):
        self.states = states
        self.transitions = transitions
        self.path = []
        self.simulation_trace = simulation_trace
        self.build_transition_matrix()

    def trace(self, message=''):
        if self.simulation_trace:
            print(message)

    def build_transition_matrix(self):
        self.transition_matrix = []
        for _ in range(len(self.states)):
            matrix_line = [0] * len(self.states)
            self.transition_matrix.append(matrix_line)
        for state in self.states:
            possible_states, probabilities = self.allowed_transitions(state)
            for possible_state, prob in zip(possible_states, probabilities):
                self.transition_matrix[self.states.index(state)][self.states.index(possible_state)] = prob

    def simulation_init(self):
        self.actual_state = self.states[0]
        self.path = [self.actual_state]
        self.trace(f'>>> Simulation initialized: initial state: {self.actual_state}')

    def simulation_step(self):
        possible_states, probabilities = self.allowed_transitions(self.actual_state)
        self.print_allowed_transitions(possible_states, probabilities)
        next_state = np.random.choice(possible_states, p=probabilities)
        self.trace(f'>>> Transition chosen: {self.actual_state} -> {next_state}')
        self.actual_state = next_state
        self.path.append(self.actual_state)
        return self.actual_state

    def verify_property_linear_system(self, property):
        transition_matrix = np.array(self.transition_matrix)
        property_index = self.states.index(property)
        indices_to_delete = [property_index]

        for i in range(transition_matrix.shape[0]):
            if i != property_index and transition_matrix[i, i] == 1:
                indices_to_delete.append(i)

        A_temp = np.delete(transition_matrix, indices_to_delete, axis=0)
        A = np.delete(A_temp, indices_to_delete, axis=1)
        b = np.delete(transition_matrix[:, property_index], indices_to_delete)
        y = np.linalg.solve(np.identity(A.shape[0]) - A, b)

        return y[0]
    

    def verify_property_iterative(self, target_states, initial_state, epsilon=1e-4, max_iterations=10000):
        if isinstance(target_states, str):
            if ',' in target_states:
                target_states = [s.strip() for s in target_states.split(',')]
            else:
                target_states = [target_states]
        for t in target_states:
            if t not in self.states:
                raise Exception(f"Error: state '{t}' not declared")
        target_indices = [self.states.index(t) for t in target_states]
        n = len(self.states)
        
        if not hasattr(self, 'transition_matrix'):
            self.build_transition_matrix()
        P = np.array(self.transition_matrix)
        
        p = np.zeros(n)
        for idx in target_indices:
            p[idx] = 1.0

        for it in range(max_iterations):
            p_new = np.copy(p)
            for i in range(n):
                if i in target_indices or np.isclose(P[i, i], 1.0):
                    continue
                p_new[i] = np.dot(P[i, :], p)
            for idx in target_indices:
                p_new[idx] = 1.0
            if np.max(np.abs(p_new - p)) < epsilon:
                p = p_new
                break
            p = p_new
        return p[self.states.index(initial_state)]

    def verify_property_smc_quant(self, property, epsilon, delta, number_steps=20):
        N = np.ceil( (np.log(2) - np.log(delta)) / (2*epsilon)**2 )
        count = 0
        self.simulation_trace = False
        for k in range(int(N)):
            is_property_verified = False
            self.simulation_init()
            i = 0
            while not is_property_verified and i < number_steps:
                is_property_verified = (self.actual_state == property)
                self.simulation_step()
                i += 1
            if is_property_verified:
                count += 1
        self.simulation_trace = True
        gama = count / N
        return gama
    
    def verify_property_smc_qual(
            self, 
            property, 
            theta, 
            epsilon, 
            alpha=0.01, 
            beta=0.01, 
            max_simulations=10000, 
            max_steps_per_simulation=1000):
        
        gamma1 = theta - epsilon
        gamma0 = theta + epsilon

        A = (1 - beta) / alpha
        B = beta / (1 - alpha)

        m = 0   # total number of simulations
        dm = 0  # number of simulations accepted

        self.simulation_trace = False
        hypothesis_accepted = False


        while not hypothesis_accepted and m < max_simulations:
            is_property_verified = False
            self.simulation_init()
            i = 0

            while not is_property_verified and i < max_steps_per_simulation:
                is_property_verified = (self.actual_state == property)
                self.simulation_step()
                i += 1
            
            if is_property_verified:
                dm += 1

            m += 1
            Rm = ( (gamma1 ** dm) * (1 - gamma1) ** (m - dm) ) / ( (gamma0 ** dm) * (1 - gamma0) ** (m - dm) )
            if Rm >= A or Rm <= B:
                hypothesis_accepted = True


            if m % 100 == 0:
                print(f'>>> [LOG] Simulation {m} - Rm {Rm} - A {A} - B {B}')

        self.simulation_trace = True

        if hypothesis_accepted and Rm >= A:
            return 1
        elif hypothesis_accepted and Rm < B:
            return 0
        else:
            return -1


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
        self.trace('>>> Possible Transitions')
        for i in range(len(possible_states)):
            self.trace(f'{self.actual_state} -> {possible_states[i]}: {probabilities[i]*100}%')
        self.trace()

    def expected_reward_MC(self, init_state, target_states, num_simulations=10000, max_iterations=1000):
        p = self.verify_property_iterative(target_states, init_state)

        if abs(p - 1) > 1e-3:
            return 0

        total_reward = 0.0
        for sim in range(num_simulations):
            current_state = init_state
            cumulative_reward = 0
            reached_target = False

            for _ in range(max_iterations):
                if current_state in target_states:
                    reached_target = True
                    break  
                succ, probs = self.allowed_transitions(current_state)
                if not succ:
                    break
                next_state = np.random.choice(succ, p=probs)
                if next_state != current_state:
                    cumulative_reward += self.state_rewards.get(current_state, 0)
                current_state = next_state
            if not reached_target:
                return 0
            total_reward += cumulative_reward
        return total_reward / num_simulations

   
class MarkovDecisionProcess(MarkovChain):
    def __init__(self, states, actions, transitions, action_transitions):
        self.actions = actions
        self.actions.append('no_action')
        self.action_transitions = action_transitions
        super().__init__(states, transitions)
        self.last_action = None          
        self.last_next_state = None      

    def simulation_init(self):
        super().simulation_init()
        next_actions = self.possible_actions(self.actual_state)
        return next_actions

    def build_transition_matrix(self):
        state_action_pairs = []

        for state in self.states:
            actions = list(self.possible_actions(state))
            for action in actions:
                state_action_pairs.append((state, action))
        
        transition_matrix = np.empty((0, len(self.states)))
        for (state, action) in state_action_pairs:
            transition_matrix_line = np.zeros(len(self.states))
            possible_states, probabilities = self.allowed_transitions(state, action)
            for possible_state, prob in zip(possible_states, probabilities):
                transition_matrix_line[self.states.index(possible_state)] = prob
            transition_matrix = np.vstack((transition_matrix, transition_matrix_line))
    
        self.transition_matrix = transition_matrix
        self.actions_by_state = state_action_pairs

    def verify_property_linear(self, property):
        transition_matrix = deepcopy(self.transition_matrix)

        property_index = self.states.index(property)

        rows_to_delete = []
        columns_to_delete = [property_index]

        # searching for indexes to delete
        for i in range(len(self.actions_by_state)):
            if self.actions_by_state[i][0] == property:
                rows_to_delete.append(i)

        A_temp = np.delete(transition_matrix, rows_to_delete, axis=0)

        b = deepcopy(A_temp[:, property_index])

        A = -1*np.delete(A_temp, columns_to_delete, axis=1)

        actions_states_mapping = np.delete(np.array(self.actions_by_state), rows_to_delete, axis=0)

        states_without_property = deepcopy(self.states)
        states_without_property.remove(property)

        for i in range(len(actions_states_mapping)):
            state, action = actions_states_mapping[i]
            A[i, states_without_property.index(state)] += 1 


        for i, state in enumerate(states_without_property):
            if state != property:
                line1 = np.zeros(A.shape[1])
                line1[i] = -1
                line2 = np.zeros(A.shape[1])
                line2[i] = 1
                A = np.vstack((A, line1))
                A = np.vstack((A, line2))

                b = np.append(b, [-1])
                b = np.append(b, [0])

        c = np.ones(A.shape[1])

        res = linprog(c, A_ub=-1*A, b_ub=-1*b, method='highs')

        return res.x[0]


    def allowed_transitions(self, state, action):
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
        self.trace(f'>>> Action performed: {action}')
        possible_states, probabilities = self.allowed_transitions(self.actual_state, action)
        self.print_allowed_transitions(possible_states, probabilities)
        next_state = np.random.choice(possible_states, p=probabilities)
        self.trace(f'>>> Transition chosen: {self.actual_state} -> {next_state}\n')
        self.actual_state = next_state
        self.path.append(self.actual_state)
        self.last_action = action
        self.last_next_state = next_state
        next_actions = self.possible_actions(self.actual_state)
        return self.actual_state, next_actions

    def possible_actions(self, state):
        possible_actions = set()
        for transition in self.action_transitions:
            if transition['from'] == state:
                possible_actions.add(transition['action'])
        return possible_actions
    
    def q_learning(self, gamma=0.5, simulations_number=10000):
        index = lambda s, a: self.states.index(s) * len(self.actions) + self.actions.index(a)
        Q = np.zeros(len(self.states) * len(self.actions))

        self.simulation_trace = False
        for i in range(simulations_number):
            alpha = 1/(i + 1)

            if i % 100 == 0:
                self.simulation_init()

            state = self.actual_state
            possible_actions = self.possible_actions(state)

            action = np.random.choice(list(possible_actions))
            next_state, next_possible_actions = self.simulation_step(action)

            Qtemp = deepcopy(Q)
            maxQ = 0
            for _action in next_possible_actions:
                if Q[index(next_state, _action)] > maxQ:
                    maxQ = Q[index(next_state, _action)]

            delta = self.state_rewards[state] + gamma * maxQ - Q[index(state, action)]
            Qtemp[index(state, action)] = Q[index(state, action)] + alpha*delta

            Q = deepcopy(Qtemp)
        
        self.simulation_trace = True

        return Q
