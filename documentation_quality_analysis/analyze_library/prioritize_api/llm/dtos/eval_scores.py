class EvalScores:
    def __init__(self, recall: float, precision: float, accuracy: float, f_measure: float):
        self.recall: float = recall
        self.precision: float = precision
        self.accuracy: float = accuracy
        self.f_measure: float = f_measure
