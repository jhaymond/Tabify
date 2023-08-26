'''

'''
from Tabify.src.models.guitar import Guitar

class Tab:
    def __init__(self, fingerings, guitar = Guitar(), line_len = 80):
        self.fingerings = fingerings
        self.guitar = guitar
        self.line_len = line_len
    
    def __tablature(self, fingering):
        flattened_notes = [note for finger in fingering.fingers.values() for note in finger]
        is_double_length = len([n for n in flattened_notes if n > 10]) > 0
        notes = sorted(flattened_notes, key = lambda v: (v[1], -v[0]))
        result = []
        for string in range(1, self.guitar.num_strings + 1):
            str_value = ''
            if len(notes) > 0 and string == notes[0][1]:
                str_value = str(notes[0][0])
                notes = [n for n in notes if n[1] != string]
            else:
                str_value = '-'
            
            if is_double_length:
                str_value += '-'
            result += [str_value]

        return result.reverse()
    
    def __str__(self):
        tab_str_lines = self.guitar.as_tablature()
        completed_line_count = 0
        for f in self.fingerings:
            # todo: there will be another loop layer once we have measures implemented
            # this will be important for finding bar lines
            fingering_tab = self.__tablature(f)
            for s in self.guitar.num_strings:
                # todo: using chord offsets will be vital for determining spacing
                tab_str_lines[completed_line_count + s] += fingering_tab[s] + '-'
        
        # todo: establish barline
        if False:
            for s in self.guitar.num_strings:
                tab_str_lines[completed_line_count + s] += '|'
        
        if len(tab_str_lines[completed_line_count]) > self.line_len:
            # todo: move current measure to next line
            tab_str_lines += self.guitar.as_tablature()
            completed_line_count += self.guitar.num_strings

        return '\n'.join(tab_str_lines)