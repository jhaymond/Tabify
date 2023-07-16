'''

'''
from music21.pitch import Pitch
from music21.interval import Interval

class Guitar:
    '''
    
    '''
    def __init__(self, tuning = None, num_frets = 24, num_strings = 6):
        if tuning is None:
            self.tuning = [Pitch('E2'), Pitch('A2'), Pitch('D3'), Pitch('G3'), Pitch('B3'), Pitch('E4')]
            if num_strings in (7, 8):
                self.tuning.insert(0, Pitch('B1'))
            if num_strings == 8:
                self.tuning.push(Pitch('A4'))
        else:
            self.tuning = tuning
        self.num_frets = num_frets
        self.num_strings = num_strings
    
    def range_size(self):
        return Interval(self.lowest_pitch(), self.highest_pitch()).semitones

    def lowest_pitch(self):
        return self.tuning[0]
    
    def highest_pitch(self):
        return self.tuning[-1].transpose(self.num_frets)
    
    def is_barreable(self, notes):
        for i in range(self.num_frets):
            if len([n for n in notes if n not in [t.transpose(i) for t in self.tuning]]) < 4:
                return True
        return False

    def __str__(self):
        return ''.join([p.name for p in self.tuning])