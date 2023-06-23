from chord import Chord
from fingering import Fingering
from music21 import converter, interval

class Transcriber:
    def __init__(self, guitar):
        self.guitar = guitar
        self.saved_fingerings = dict()

    def transcribe(self, song):
        notes = converter.parse(song).flatten().getElementsByClass('Note', 'Chord')
        # todo: simplify the chords/detect optimal range?
        return self.evaluate_song(None, 0, notes, dict(), [1 for i in range(4)])

    def get_fingerings(self, remaining_chord, fingering_in_progress = []):
        '''
        
        '''
        fret_range_set = {f[0] for f in fingering_in_progress if f[0] != 0}
        used_strings = [n[1] - 1 for n in fingering_in_progress]
        if len(fret_range_set) == 0:
            min_fret = 1
            max_fret = self.guitar.num_frets
            usable_strings = [i
                              for i
                              in range(self.guitar.num_strings)
                              if i not in used_strings]
        elif len(fret_range_set) == 4:
            # all fingers are being used so we have to start barreing
            min_fret = max_fret = min(fret_range_set)
            max_open_string = max([f[1] for f in fingering_in_progress if f[0] == 0])
            usable_strings = [i
                              for i
                              in range(self.guitar.num_strings)
                              if i not in used_strings and i > max_open_string]
        else:
            min_fret = max([1, max(fret_range_set) - 4])
            max_fret = min([self.guitar.num_frets, min(fret_range_set) + 4])
            usable_strings = [i
                              for i
                              in range(self.guitar.num_strings)
                              if i not in used_strings]

        curr_note = remaining_chord.notes[0]
        viable_notes = []
        for string in usable_strings:
            string_tuning = self.guitar.tuning[string]
            if string_tuning == curr_note.pitch or (string_tuning.transpose(min_fret) <= curr_note.pitch and curr_note.pitch <= string_tuning.transpose(max_fret)):
                viable_notes.append((interval.Interval(string_tuning, curr_note.pitch).semitones, string + 1))

        fingerings = []
        for note in viable_notes:
            if len(remaining_chord.notes) <= 1:
                # todo: we need to get all possible finger combinations if not all fingers are used
                fingerings += self.get_fingerings_for_fretting(fingering_in_progress + [note])
            else:
                fingerings += self.get_fingerings(Chord(remaining_chord.notes[1:]), fingering_in_progress + [note])

        return fingerings

    def get_fingerings_for_fretting(self, fretting, starting_finger = 1, fingering_in_progress = None):
        if len(fretting) == 0:
            return [Fingering(fingering_in_progress)]
        
        fingerings = []
        fingered_frets = fretting
        if starting_finger == 1:
            fingered_frets = [f for f in fretting if f[0] != 0]
            barre_fret = min([f[0] for f in fingered_frets])
            is_barreable = max([f[1] for f in fretting if f[0] == 0]) < min([f[1] for f in fingered_frets if f[0] == barre_fret])
            must_be_barred = len(fingered_frets) > 4

            if must_be_barred and not is_barreable:
                return []

            if fingering_in_progress is None:
                fingering_in_progress = dict()

            if is_barreable:
                fingering_in_progress[starting_finger] = [f for f in fretting if f[0] == barre_fret]
                fingerings += self.get_fingerings_for_fretting([f for f in fingered_frets if f[0] != barre_fret], 2, fingering_in_progress)

            if must_be_barred:
                return fingerings
        
        skippable_fingers = (4 - starting_finger) - len(fingered_frets)
        note = fingered_frets[0]
        for i in range(skippable_fingers):
            finger = starting_finger + i
            # todo: check if this finger and the previous fingers are close enough
            fingerings += self.get_fingerings_for_fretting([f for f in fingered_frets if f != note], finger + 1, fingering_in_progress + (finger, note))

        return fingerings

    def evaluate_song(self, prev_fingering, cost, remaining_song, saved_transitions, modifiers):
        if len(remaining_song) == 0:
            return (cost, [prev_fingering])

        curr_notes = Chord(remaining_song.pop(0))
        saved_fingerings_idx = str(curr_notes)
        saved_transitions_idx = str(prev_fingering.chord) + saved_fingerings_idx

        if saved_transitions_idx in saved_transitions.keys():
            transition = saved_transitions[saved_transitions_idx]
            return self.evaluate_song(transition[1],
                                      cost + transition[1].stretch_cost + transition[0],
                                      remaining_song,
                                      saved_transitions,
                                      # todo: it's more complicated than this
                                      [1 if transition[1].finger_is_active(i) else 2 for i in range(1, 5)])
        results = []
        if saved_fingerings_idx in self.saved_fingerings.keys():
            curr_fingerings = self.fingerings_by_chord[saved_fingerings_idx]
        else:
            curr_fingerings = self.get_fingerings(curr_notes)
        for f in curr_fingerings:
            transition_cost = 0
            saved_transitions_branch = saved_transitions
            if prev_fingering is not None:
                transition_cost = prev_fingering.calculate_finger_movement(f, modifiers)
                saved_transitions_branch = dict(saved_transitions)
                saved_transitions_branch[saved_transitions_idx] = (transition_cost, f)
            result = self.evaluate_song(f,
                                        cost + f.stretch_cost + transition_cost,
                                        remaining_song,
                                        saved_transitions_branch,
                                        [1 if f.finger_is_active(i) else 2 for i in range(1, 5)])
            results.append(result)

        best = min(results, key = lambda r: r[0])
        return (best[0], [prev_fingering] + best[1])
