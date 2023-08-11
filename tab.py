'''

'''
from guitar import Guitar

class Tab:
    def __init__(self, fingerings, guitar = Guitar()):
        self.fingerings = fingerings
        self.guitar = guitar
    
    def format(self):
        for f in self.fingerings:
            yield str(f)
    
    def __str__(self):
        return ' | '.join([f.tablature() for f in self.fingerings])