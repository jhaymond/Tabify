'''
This module contains the Fingering class which is essential for representing
guitar chords.
'''

import math

class Fingering:
    '''
    Class for a fingering pattern on a guitar fretboard.
    notes: a list of finger positions (Tuple<Integer, Integer>) to be 
    included in the fingering
    '''
    def __init__(self, notes = None):
        if notes is None:
            self.fingers = {}
        else:
            self.fingers = notes
            self.stretch_cost = self.__calculate_stretch()
        self.chord = None

        self.from_chords = {}
        self.to_chords = {}
        
        self.finger_distance_matrix = [
            [0, self.__finger_distance((0,1), (3,6)), self.__finger_distance((0,1), (4,6)), self.__finger_distance((0,1), (5,6))],
            [self.__finger_distance((0,1), (3,6)), 0, self.__finger_distance((0,1), (2,6)), self.__finger_distance((0,1), (4,6))],
            [self.__finger_distance((0,1), (4,6)), self.__finger_distance((0,1), (2,6)), 0, self.__finger_distance((0,1), (1,6))],
            [self.__finger_distance((0,1), (5,6)), self.__finger_distance((0,1), (4,6)), self.__finger_distance((0,1), (1,6)), 0]
        ]
    
    def set_chord(self, chord):
        self.chord = chord
        self.from_chords[str(chord)] = [(0, self)]
        self.to_chords[str(chord)] = [(0, self)]

    def get_notes(self):
        return [note for finger in self.fingers.values() for note in finger]

    def finger_is_active(self, finger_no):
        '''
        A simple Boolean calculation to determine whether a finger is being 
        used in a fingering pattern.
        finger_no: an Integer representing which finger (1 for index to 4 
        for pinky)
        Returns: True or False
        '''
        return finger_no in self.fingers
    
    def is_possible(self):
        for i in range(1, 4):
            if i in self.fingers:
                for j in range(i + 1, 5):
                    if j in self.fingers:
                        if self.finger_distance_matrix[i-1][j-1] < self.__finger_distance(self.fingers[i][0], self.fingers[j][0]):
                            return False
        return True

    def __calculate_stretch(self):
        '''
        Calculates the relative difficulty of this fingering position based on
        how much the fingers have to stretch.
        Returns: a Decimal value
        '''
        finger_stretch = 0

        keys = sorted([k for k in self.fingers if k is not None])
        if not keys:
            return 0
        
        f_curr = keys[0]
        for f_next in keys[1:]:
            if self.fingers[f_next] is not None:
                finger_stretch += self.__finger_distance(self.fingers[f_curr][0], self.fingers[f_next][0], f_next - f_curr)
                f_curr = f_next

        return finger_stretch

    def __finger_distance(self, f_1, f_2, modifier=1):
        '''
        Calculation for the Euclidean distance between two fingertips on the fretboard.
        f_1: a tuple representing a finger, in the form (fret_no, string_no)
        f_2: a tuple representing another finger, in the form (fret_no, string_no)
        modifier: a factor representing how much easier this distance should be 
        considered than normal
        Returns: a Decimal value
        '''
        return math.sqrt((f_2[0]*2.5-f_1[0]*2.5)**2+(f_2[1]-f_1[1])**2)/modifier

    def transition(self, other):
        '''
        Calculates the relative difficulty of moving from this fingering to another specified 
        fingering.
        other: a Fingering object representing the chord being moved to
        finger_inactivity: an array representing how long each finger has been in-place
        Returns: a Decimal value
        '''
        finger_movement = 0

        for i in range(4):
            if i + 1 in self.fingers and i + 1 in other.fingers:
                curr_finger = self.fingers[i + 1]
                next_finger = other.fingers[i + 1]
                finger_movement += self.__finger_distance(
                    curr_finger[0],
                    next_finger[0],
                    1)
        return finger_movement

    def tablature(self, num_strings = 6, vertical = False):
        flattened_notes = [note for finger in self.fingers.values() for note in finger]
        notes = sorted(flattened_notes, key = lambda v: (v[1], -v[0]))
        result = ''
        for i in range(1, num_strings + 1):
            if len(notes) > 0 and i == notes[0][1]:
                result += str(notes[0][0])
                notes = [n for n in notes if n[1] != i]
            else:
                result += '-'
            
            if vertical:
                result += '\n'
        return result
