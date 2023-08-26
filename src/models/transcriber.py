'''
Defines the Transcriber class, which can use the transcribe() function to convert a sheet music file
into a Tab object.
'''
from music21 import converter
from Tabify.src.models.chord import Chord
from Tabify.src.models.tab import Tab
from Tabify.src.models.transcriber_configs import TranscriberConfigs

# todo: set up the fingering list in a way that can more easily be parsed by the tab object

class Transcriber:
    '''
    A class for converting sheet music files into Tab objects.
    guitar: a Guitar object; defaults to the default Guitar object values
    '''
    def __init__(self, configs = TranscriberConfigs()):
        self.configs = configs
        self.saved_fingerings = {}
        self.notes = []

    def transcribe(self, input_file):
        '''
        The primary function of the class; takes the source file and returns the result of the
        transcription process.
        song: a valid file location of one of the following formats:
        '''
        song_components = ['Note', 'Chord']
        notes = converter.parse(input_file).flatten().getElementsByClass(song_components)
        if not notes:
            return []
        self.notes = self.prepare_song(notes)
        results = self.evaluate_song()
        return Tab(results, self.configs.guitar)

    def evaluate_song(self):
        optimal_paths = []

        for chord in self.notes:
            if not optimal_paths:
                optimal_paths = [([f], self.configs.stretch_weight * f.stretch_cost)
                                 for f
                                 in self.saved_fingerings[str(Chord(chord))]]
                continue

            new_optimal_paths = []
            for fingering in self.saved_fingerings[str(Chord(chord))]:
                new_optimal_path = ()
                for path in optimal_paths:
                    new_path = (path[0] + [fingering],
                                path[1] +
                                self.configs.transition_weight * path[0][-1].transition(fingering) +
                                self.configs.stretch_weight * fingering.stretch_cost)
                    if not new_optimal_path or new_path[1] < new_optimal_path[1]:
                        new_optimal_path = new_path
                new_optimal_paths.append(new_optimal_path)

            optimal_paths = new_optimal_paths
        return min(optimal_paths, key = lambda p: p[1])[0]

    def prepare_song(self, notes):
        '''
        
        '''
        prepared_notes = []
        idx = 0
        current_offset = 0
        transpose_steps = self.configs.guitar.get_transposition(notes)
        for note in notes:
            if note.isChord:
                new_notes = [n.transpose(transpose_steps) for n in note.notes]
            else:
                new_notes = [note.transpose(transpose_steps)]

            if len(prepared_notes) == 0:
                prepared_notes.append(new_notes)
                current_offset = note.offset
            elif current_offset != note.offset:
                # gather all viable fingerings for all the chords in the song
                # todo: self.configs.guitar.make_chord_playable(prepared_notes[idx])
                new_chord = Chord(prepared_notes[idx])
                if new_chord not in self.saved_fingerings:
                    new_fingerings = self.configs.guitar.get_fingerings(prepared_notes[idx])
                    self.saved_fingerings[str(new_chord)] = new_fingerings

                idx += 1
                current_offset = note.offset
                prepared_notes.append(new_notes)
            else:
                prepared_notes[idx].extend(new_notes)

        final_chord = Chord(prepared_notes[idx])
        if final_chord not in self.saved_fingerings:
            final_fingerings = self.configs.guitar.get_fingerings(prepared_notes[idx])
            self.saved_fingerings[str(final_chord)] = final_fingerings

        return prepared_notes
