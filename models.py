class MarkovChain:
    def __init__(self):
        self.states = []
        self.transitions = []

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