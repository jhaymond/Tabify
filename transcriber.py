'''
Defines the Transcriber class, which can use the transcribe() function to convert a sheet music file
into a Tab object.
'''
from chord import Chord
from guitar import Guitar
from fingering import Fingering
import music21.chord
from music21 import converter
from music21.pitch import Pitch
from music21.interval import Interval

OCTAVE = 12
NUM_FINGERS = 4
MAX_REACH = 4
ROOT = 1
NINTH = 2
THIRD = 3
ELEVENTH = 4
FIFTH = 5
THIRTEENTH = 6
SEVENTH = 7
MAX_MODIFIER = 3

class Transcriber:
    '''
    A class for converting sheet music files into Tab objects.
    guitar: a Guitar object; defaults to the default Guitar object values
    '''
    def __init__(self, guitar = Guitar()):
        self.guitar = guitar
        self.saved_fingerings = {}
        self.notes = []

    def transcribe(self, song):
        '''
        The primary function of the class; takes the source file and returns the result of the
        transcription process.
        song: a valid file location of one of the following formats:
        '''
        song_components = ['Note', 'Chord']
        notes = converter.parse(song).flatten().getElementsByClass(song_components)
        #notes = music21.corpus.parse('bach/bwv66.6').flatten().getElementsByClass(song_components)
        if not notes:
            return []
        self.prepare_song(notes)
        return self.evaluate_song(None, 0, self.notes, {}, [1 for i in range(NUM_FINGERS)])

    def get_transposition(self, notes):
        '''
        Determine whether it is necessary to transpose a song into the playable range of the guitar,
        and return the optimal transposition interval (in semitones) if so.
        notes: a list of music21 Note objects
        '''
        song_range = (min(notes, key = lambda n: n.pitch).pitch,
                      max(notes, key = lambda n: n.pitch).pitch)
        guitar_range = (self.guitar.lowest_pitch(), self.guitar.highest_pitch())
        low_overshoot = Interval(song_range[0], guitar_range[0]).semitones
        high_undershoot = Interval(song_range[1], guitar_range[1]).semitones

        if Interval(song_range[0], song_range[1]).semitones > self.guitar.range_size():
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


    def prepare_song(self, notes):
        '''
        
        '''
        self.notes = []
        idx = 0
        transpose_steps = self.get_transposition(notes)

        for note in notes:
            if note.isChord:
                new_notes = [n.transpose(transpose_steps) for n in note.notes]
            else:
                new_notes = [note.transpose(transpose_steps)]

            if len(self.notes) == 0:
                self.notes.append(new_notes)
            elif self.notes[idx][0].offset != note.offset:
                idx += 1
                self.notes.append(new_notes)
            else:
                self.notes[idx].extend(new_notes)

    def simplify_chord(self, chord):
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

        chord_root = music21.chord.Chord(notes_by_name.keys()).root()
        intervals = {int(Interval(chord_root, Pitch(p)).name[1:]): p for p in notes_by_name}
        priority = [ROOT, THIRD, SEVENTH, THIRTEENTH, ELEVENTH, NINTH, FIFTH]
        prioritized_notes = [bass_note, high_note] + [intervals[i]
                                                      for i in priority
                                                      if i in intervals
                                                      and intervals[i] not in [bass_note,
                                                                               high_note]]

        if len(notes_by_name) > self.guitar.num_strings:
            notes_by_name = {k: v
                             for k, v in notes_by_name
                             if k in prioritized_notes[:self.guitar.num_strings]}

        new_chord = [chord[0]] + [notes_by_name[n][-1]
                                  for n in notes_by_name
                                  if notes_by_name[n][-1].name
                                  not in [bass_note, high_note]] + [chord[-1]]
        max_interval = Interval(self.guitar.tuning[0], self.guitar.tuning[-1]).semitones + MAX_REACH
        chord_breadth = Interval(new_chord[0].pitch, new_chord[-1].pitch).semitones

        if new_chord[0].pitch < self.guitar.lowest_pitch():
            # this except add it to new_chord
            new_chord[0].pitch = new_chord[0].pitch.transpose(OCTAVE)
            for note in new_chord[1:]:
                if note.pitch < new_chord[0].pitch:
                    note.pitch = note.pitch.transpose(OCTAVE)
        if chord_breadth > max_interval and new_chord[0].pitch != self.guitar.tuning[0]:
            new_chord[-1].pitch = new_chord[-1].pitch.transpose(-OCTAVE)
            for note in new_chord[::-1][:-1]:
                if note.pitch > new_chord[-1].pitch:
                    note.pitch = note.pitch.transpose(-OCTAVE)


        while not self.guitar.is_barreable(new_chord) and len(new_chord) > NUM_FINGERS:
            new_chord = [n for n in new_chord if n.name in prioritized_notes[:len(new_chord)-1]]

        return new_chord

    def get_fingerings(self, remaining_chord, fingering_in_progress = None):
        '''
        
        '''
        if fingering_in_progress is None:
            fingering_in_progress = []
        fret_range_set = {f[0] for f in fingering_in_progress if f[0] != 0}
        used_strings = [n[1] - 1 for n in fingering_in_progress]
        if len(fret_range_set) == 0:
            min_fret = 1
            max_fret = self.guitar.num_frets
            usable_strings = [i
                              for i
                              in range(self.guitar.num_strings)
                              if i not in used_strings]
        elif len(fret_range_set) == NUM_FINGERS:
            # all fingers are being used so we have to start barreing
            min_fret = max_fret = min(fret_range_set)
            max_open_string = max([f[1] for f in fingering_in_progress if f[0] == 0])
            usable_strings = [i
                              for i
                              in range(self.guitar.num_strings)
                              if i not in used_strings and i > max_open_string]
        else:
            min_fret = max([1, max(fret_range_set) - MAX_REACH])
            max_fret = min([self.guitar.num_frets, min(fret_range_set) + MAX_REACH])
            usable_strings = [i
                              for i
                              in range(self.guitar.num_strings)
                              if i not in used_strings]

        curr_note = remaining_chord[0]
        viable_notes = []
        for string in usable_strings:
            target_pitch = curr_note.pitch
            string_tuning = self.guitar.tuning[string]
            min_fret_pitch = string_tuning.transpose(min_fret)
            max_fret_pitch = string_tuning.transpose(max_fret)

            if string_tuning == target_pitch or min_fret_pitch <= target_pitch <= max_fret_pitch:
                note_fret = Interval(string_tuning, curr_note.pitch).semitones
                viable_notes.append((note_fret, string + 1))

        fingerings = []
        for note in viable_notes:
            new_remaining_chord = remaining_chord[1:]
            new_fingering_in_progress = fingering_in_progress + [note]

            if len(new_remaining_chord) == 0:
                fingerings += self.get_fingerings_for_fretting(new_fingering_in_progress)
            else:
                fingerings += self.get_fingerings(new_remaining_chord, new_fingering_in_progress)

        return fingerings

    def get_fingerings_for_fretting(self, fretting, starting_finger=1, fingering_in_progress=None):
        '''
        
        '''
        if not fretting:
            new_fingering = Fingering(fingering_in_progress)
            if new_fingering.is_possible():
                return [Fingering(fingering_in_progress)]
            return []

        fingerings = []
        fingered_frets = fretting
        if starting_finger == 1:
            # initialization and barre chord checks
            fingered_frets = sorted([f for f in fretting if f[0] != 0])
            if len(fretting) > len(fingered_frets):
                fingering_in_progress = {None: [f for f in fretting if f not in fingered_frets]}
            else:
                fingering_in_progress = {}
            
            if not fingered_frets:
                return [Fingering(fingering_in_progress)]

            barre_fret = min([f[0] for f in fingered_frets])
            max_open_string = max([f[1] for f in fretting if f[0] == 0] + [0])
            barreable_strings = [f[1] for f in fingered_frets if f[0] == barre_fret]

            no_barre_gaps = max_open_string < min(barreable_strings)
            multiple_strings_barreable = len(barreable_strings) > 1
            enough_strings_barreable = len(fingered_frets) - len(barreable_strings) < NUM_FINGERS

            is_barreable = no_barre_gaps and multiple_strings_barreable and enough_strings_barreable
            must_be_barred = len(fingered_frets) > NUM_FINGERS

            if must_be_barred and not is_barreable:
                return []

            # barre chords
            if is_barreable:
                new_fretting = [f for f in fingered_frets if f[0] != barre_fret]
                new_starting_finger = 2
                new_fingering_in_progress = {**fingering_in_progress,
                                             **{1: [f for f in fretting if f[0] == barre_fret]}}
                fingerings += self.get_fingerings_for_fretting(new_fretting,
                                                               new_starting_finger,
                                                               new_fingering_in_progress)

            if must_be_barred:
                return fingerings

        # all alternative frettings based on available fingers
        startable_fingers = 1 + (1 + NUM_FINGERS - starting_finger) - len(fingered_frets)
        note = fingered_frets[0]
        for i in range(startable_fingers):
            finger = starting_finger + i
            new_fretting = [f for f in fingered_frets if f != note]
            new_fingering_in_progress = {**fingering_in_progress, **{finger: [note]}}
            fingerings += self.get_fingerings_for_fretting(new_fretting,
                                                           finger + 1,
                                                           new_fingering_in_progress)

        return fingerings

    def evaluate_song(self, prev_fingering, cost, remaining_song, saved_transitions, modifiers):
        '''
        
        '''
        if len(remaining_song) == 0:
            print('recursion end!')
            return (cost, [prev_fingering])

        curr_notes = remaining_song[0]
        fingering_duration = min([n.quarterLength for n in curr_notes])

        chord = Chord(curr_notes)
        saved_fingerings_idx = str(chord)
        saved_transitions_idx = None
        if prev_fingering:
            prev_chord_idx = str(prev_fingering.chord)
            if prev_chord_idx == saved_fingerings_idx:
                result = self.evaluate_song(prev_fingering,
                            cost,
                            remaining_song[1:],
                            saved_transitions,
                            [1
                            if prev_fingering.finger_is_active(i + 1)
                            else min([modifiers[i] + fingering_duration, MAX_MODIFIER])
                            for i in range(NUM_FINGERS)])
                return (result[0], [prev_fingering] + result[1])
            saved_transitions_idx = prev_chord_idx + '_' + saved_fingerings_idx

        if saved_transitions_idx in saved_transitions:
            transition = saved_transitions[saved_transitions_idx]
            fingering_duration = min([n.quarterLength for n in curr_notes])
            result = self.evaluate_song(transition[1],
                                      cost + transition[1].stretch_cost + transition[0],
                                      remaining_song[1:],
                                      saved_transitions,
                                      [1
                                       if transition[1].finger_is_active(i + 1)
                                       else min([modifiers[i] + fingering_duration, MAX_MODIFIER])
                                       for i in range(NUM_FINGERS)])
            return (result[0], [prev_fingering] + result[1])
        
        results = []
        if saved_fingerings_idx in self.saved_fingerings:
            curr_fingerings = self.saved_fingerings[saved_fingerings_idx]
        else:
            curr_fingerings = []
            while not curr_fingerings:
                curr_fingerings = self.get_fingerings(curr_notes)
                if not curr_fingerings:
                    curr_notes = self.simplify_chord(curr_notes)
            for fingering in curr_fingerings:
                fingering.chord = chord
            self.saved_fingerings[saved_fingerings_idx] = curr_fingerings
        for fingering in curr_fingerings:
            transition_cost = 0
            saved_transitions_branch = saved_transitions
            if prev_fingering is not None:
                transition_cost = prev_fingering.calculate_finger_movement(fingering, modifiers)
                saved_transitions_branch = dict(saved_transitions)
                saved_transitions_branch[saved_transitions_idx] = (transition_cost, fingering)
            result = self.evaluate_song(fingering,
                                        cost + fingering.stretch_cost + transition_cost,
                                        remaining_song[1:],
                                        saved_transitions_branch,
                                        [1
                                         if fingering.finger_is_active(i + 1)
                                         else min([modifiers[i] + fingering_duration, MAX_MODIFIER])
                                         for i in range(NUM_FINGERS)])
            results.append(result)
            if saved_transitions_branch != saved_transitions:
                del saved_transitions_branch

        best = sorted(results, key = lambda r: (r[0], sum([f[0] for f in r[1][0].get_notes()])))[0]

        if prev_fingering:
            return (best[0], [prev_fingering] + best[1])
        return best
