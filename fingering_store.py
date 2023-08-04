class FingeringStore:
    def __init__(self):
        self.saved_fingerings = {}
    
    def add_chord(self, chord, fingerings):
        if str(chord) in self.saved_fingerings:
            return
        self.saved_fingerings[str(chord)] = fingerings

    def add_transition(self, from_chord, to_chord):
        if str(to_chord) in self.saved_fingerings[str(from_chord)][0].to_chords:
            return

        from_fingerings = self.saved_fingerings[str(from_chord)]
        to_fingerings = self.saved_fingerings[str(to_chord)]

        for fingering in from_fingerings:
            fingering.to_chords[str(to_chord)] = sorted([(fingering.calculate_finger_movement(f), f) for f in to_fingerings], key = lambda t: (t[0], t[1].stretch_cost))
        for fingering in to_fingerings:
            fingering.from_chords[str(from_chord)] = sorted([(f.calculate_finger_movement(fingering), fingering) for f in from_fingerings], key = lambda t: (t[0], t[1].stretch_cost))

    def __getitem__(self, key):
        return self.saved_fingerings[str(key)]
    
    def __contains__(self, key):
        return self.saved_fingerings.__contains__(str(key))