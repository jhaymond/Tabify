'''

'''
from music21.pitch import Pitch
from music21.interval import Interval
from music21.chord import Chord
from Tabify.src.models.fingering import Fingering, NUM_FINGERS, OPEN, HAND, FRET

OCTAVE = 12
MAX_REACH = 4
ROOT = 1
NINTH = 2
THIRD = 3
ELEVENTH = 4
FIFTH = 5
THIRTEENTH = 6
SEVENTH = 7

class Guitar:
    '''
    
    '''
    def __init__(self, tuning = None, num_frets = 15, num_strings = 6):
        if not tuning:
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

    # todo: there might be a better way to write this, or maybe we can eliminate the need for it
    def is_barreable(self, notes):
        for i in range(self.num_frets):
            if len([n for n in notes if n not in [t.transpose(i) for t in self.tuning]]) < NUM_FINGERS:
                return True
        return False

    def make_chord_playable(self, chord):
        '''
        
        '''
        notes_by_name = {}
        for note in chord:
            if note.name not in notes_by_name:
                notes_by_name[note.name] = [note]
            else:
                notes_by_name[note.name] += [note]

        bass_note = chord[0].name
        high_note = chord[-1].name

        chord_root = Chord(notes_by_name.keys()).root()
        intervals = {int(Interval(chord_root, Pitch(p)).name[1:]): p for p in notes_by_name}
        priority = [ROOT, THIRD, SEVENTH, THIRTEENTH, ELEVENTH, NINTH, FIFTH]
        prioritized_notes = [bass_note, high_note] + [intervals[i]
                                                      for i in priority
                                                      if i in intervals
                                                      and intervals[i] not in [bass_note,
                                                                               high_note]]

        if len(notes_by_name) > self.num_strings:
            notes_by_name = {k: v
                             for k, v in notes_by_name
                             if k in prioritized_notes[:self.num_strings]}

        new_chord = [chord[0]] + [notes_by_name[n][-1]
                                  for n in notes_by_name
                                  if notes_by_name[n][-1].name
                                  not in [bass_note, high_note]] + [chord[-1]]
        max_interval = Interval(self.tuning[0], self.tuning[-1]).semitones + MAX_REACH
        chord_breadth = Interval(new_chord[0].pitch, new_chord[-1].pitch).semitones

        if new_chord[0].pitch < self.lowest_pitch():
            new_chord[0].pitch = new_chord[0].pitch.transpose(OCTAVE)
            for note in new_chord[1:]:
                if note.pitch < new_chord[0].pitch:
                    note.pitch = note.pitch.transpose(OCTAVE)
        if chord_breadth > max_interval and new_chord[0].pitch != self.tuning[0]:
            new_chord[-1].pitch = new_chord[-1].pitch.transpose(-OCTAVE)
            for note in new_chord[::-1][:-1]:
                if note.pitch > new_chord[-1].pitch:
                    note.pitch = note.pitch.transpose(-OCTAVE)

        while not self.is_barreable(new_chord) and len(new_chord) > NUM_FINGERS:
            new_chord = [n for n in new_chord if n.name in prioritized_notes[:len(new_chord)-1]]

        return new_chord

    def get_pitch_locations(self, pitch):
        return [(fret, string)
                for string, fret
                in enumerate([Interval(p, pitch).semitones for p in self.tuning])
                if 0 <= fret <= self.num_frets]

    def get_fingerings(self, chord):
        fingerings = []

        for note in chord:
            new_fingerings = []
            viable_finger_positions = self.get_pitch_locations(note.pitch)

            for position in viable_finger_positions:
                usable_fingers = OPEN if position[FRET] == 0 else HAND
                if not fingerings:
                    new_fingerings = [Fingering().try_add_position(f, position)
                                      for f
                                      in usable_fingers]

                for fingering in fingerings:
                    new_fingerings += [fingering
                                       for f
                                       in usable_fingers
                                       if fingering.try_add_position(f, position)]

            fingerings = new_fingerings

        return fingerings

    def get_transposition(self, notes):
        '''
        Determine whether it is necessary to transpose a song into the playable range of the guitar,
        and return the optimal transposition interval (in semitones) if so.
        notes: a list of music21 Note objects
        '''
        song_range = (min(notes, key = lambda n: n.pitch).pitch,
                        max(notes, key = lambda n: n.pitch).pitch)
        guitar_range = (self.lowest_pitch(), self.highest_pitch())
        low_overshoot = Interval(song_range[0], guitar_range[0]).semitones
        high_undershoot = Interval(song_range[1], guitar_range[1]).semitones

        if Interval(song_range[0], song_range[1]).semitones > self.range_size():
            # if the range is just too wide, fix the high end of the song range to the high
            # end of the guitar range; we'll finish fixing the range later in the process
            return high_undershoot

        if song_range[0] < guitar_range[0] or guitar_range[1] < song_range[1]:
            # find the fewest octaves you can transpose to get the overshoot within range
            if song_range[0] < guitar_range[0]:
                transposable_octave = low_overshoot + (OCTAVE - (low_overshoot % OCTAVE))
            else:
                transposable_octave = high_undershoot - (OCTAVE + (high_undershoot % -OCTAVE))

            if low_overshoot <= transposable_octave <= high_undershoot:
                # if you can fix the range by transposing to a different octave, do that
                return transposable_octave
            # otherwise, center the range on the fretboard
            return (high_undershoot + low_overshoot) // 2

        return 0

    def as_tablature(self):
        return [s.name + '|' for s in self.tuning].reverse()
