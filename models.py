class MarkovChain:
    def __init__(self):
        self.states = []
        self.transitions = []

    def build_simulation(self):
        pass

class MarkovDecisionProcess(MarkovChain):
    def __init__(self):
        super().__init__()
        self.actions = []
        self.transitions_with_actions = []

class TemporaryModel:
    def __init__(self):
        self.states = []
        self.actions = []
        self.transitions = []
        self.transitions_with_actions = []

    def verify_model(self):
        pass

    def generate_model(self):
        pass

# idea: use factory pattern to create the simulations
class MCSimulation(MarkovChain):
    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions
        self.actual_state = states[0]


class MDPSimulation(MarkovDecisionProcess):
    pass