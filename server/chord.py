class Chord:
    def __init__(self, notes):
        self.notes = notes
    
    def __str__(self):
        return ' '.join(self.notes)