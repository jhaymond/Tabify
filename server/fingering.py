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
    def __init__(self, notes):
        self.fingers = notes#self.__calculate_finger_placement(notes)
        self.stretch_cost = self.__calculate_stretch()

    def finger_is_active(self, finger_no):
        '''
        A simple Boolean calculation to determine whether a finger is being 
        used in a fingering pattern.
        finger_no: an Integer representing which finger (1 for index to 4 
        for pinky)
        Returns: True or False
        '''
        return finger_no in self.fingers.keys()

    # def __calculate_finger_placement(self, notes):
    #     sorted_notes = sorted(notes)
    #     fingers = dict()

    #     # separate out open notes since they won't be fingered
    #     open_notes = [n for n in sorted_notes if n[0] == 0]
    #     if len(open_notes) > 0:
    #         fingers[None] = open_notes
    #         sorted_notes = [n for n in sorted_notes if n[0] != 0]

    #     curr_finger = 1
    #     # take care of barreing if necessary
    #     if len(sorted_notes) > 4:
    #         fingers[curr_finger] = [n for n in sorted_notes if n[0] == sorted_notes[0][0]]
    #         curr_finger += 1
    #         sorted_notes = [n for n in sorted_notes if n[0] != sorted_notes[0][0]]

    #     # assign fingers to the rest of the notes sequentially
    #     for note in sorted_notes:
    #         fingers[curr_finger] = [note]
    #         curr_finger += 1

    #     return fingers

    def __calculate_stretch(self):
        '''
        Calculates the relative difficulty of this fingering position based on
        how much the fingers have to stretch.
        Returns: a Decimal value
        '''
        finger_stretch = 0

        keys = sorted([k for k in self.fingers.keys() if k is not None])
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

    def calculate_finger_movement(self, other, finger_inactivity):
        '''
        Calculates the relative difficulty of moving from this fingering to another specified 
        fingering.
        other: a Fingering object representing the chord being moved to
        finger_inactivity: an array representing how long each finger has been in-place
        Returns: a Decimal value
        '''
        finger_movement = 0

        for i, modifier in finger_inactivity:
            curr_finger = self.fingers[i]
            next_finger = other.fingers[i]
            if curr_finger is not None and next_finger is not None:
                finger_movement += self.__finger_distance(
                    curr_finger[0],
                    next_finger[0],
                    modifier)
        return finger_movement

    def tablature(self, num_strings = 6):
        flattened_notes = [note for finger in self.fingers.values() for note in finger]
        notes = sorted(flattened_notes, key = lambda v: (v[1], -v[0]))
        result = ''
        for i in range(1, num_strings + 1):
            if len(notes) > 0 and i == notes[0][1]:
                result += str(notes[0][0])
                notes = [n for n in notes if n[1] != i]
            else:
                result += '-'
        return result
