from Tabify.src.models.guitar import Guitar

class TranscriberConfigs:
    def __init__(self, tuning = None, strings = 6, frets = 15, stretch_wt = 0.5, transition_wt = 0.5):
        if stretch_wt + transition_wt != 1.0:
            raise ValueError("Transcriber weights don't add up to 1")
        self.guitar = Guitar(tuning, frets, strings)
        self.stretch_weight = stretch_wt
        self.transition_weight = transition_wt
