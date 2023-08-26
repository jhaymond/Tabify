'''
This module contains the Fingering class which is essential for representing
guitar chords.
'''

from math import sqrt

FRET = 0
STRING = 1

NUM_FINGERS = 4
OPEN = [None]
HAND = range(1, NUM_FINGERS + 1)

class Fingering:
    '''
    Class for a fingering pattern on a guitar fretboard.
    fingers: a dictionary mapping each finger number to the list of positions being held by that
    finger.
    stretch_cost: a float value representing the difficulty of playing this fingering
    '''

    def __init__(self):
        if not hasattr(Fingering, 'max_finger_distances'):
            Fingering.max_finger_distances = [
                [0,
                Fingering.distance((0,1), (3,6)),
                Fingering.distance((0,1), (4,6)),
                Fingering.distance((0,1), (5,6))],
                [Fingering.distance((0,1), (3,6)),
                0,
                Fingering.distance((0,1), (4,6))],
                Fingering.distance((0,1), (2,6)),
                [Fingering.distance((0,1), (4,6)),
                Fingering.distance((0,1), (2,6)),
                0,
                Fingering.distance((0,1), (1,6))],
                [Fingering.distance((0,1), (5,6)),
                Fingering.distance((0,1), (4,6)),
                Fingering.distance((0,1), (1,6)),
                0]
            ]
        self.fingers = {}
        self.stretch_cost = 0
    
    def cmp_positions(self, p1, p2):
        if p2[FRET] == p1[FRET]:
            return p2[STRING] - p1[STRING]
        return p2[FRET] - p1[FRET]

    def try_add_position(self, f1, position):
        existing_positions = self.get_all_positions()

        is_barred = 1 in self.fingers and len(self.fingers[1]) > 1
        top_barre_string = None if not is_barred else min([p[STRING] for p in self.fingers[1]])
        max_open_string = max([p[STRING] for p in existing_positions])

        prev_fingers = [f2 for f2 in self.fingers if f1 is not None and f2 < f1]
        next_fingers = [f2 for f2 in self.fingers if f1 is not None and f2 > f1]
        max_prev_finger = max([0] + prev_fingers)
        min_next_finger = min([NUM_FINGERS + 1] + next_fingers)
        passes_prev_finger = max_prev_finger > 0 and self.cmp_positions(self.fingers[max_prev_finger][0], position) > 0
        passes_next_finger = min_next_finger < NUM_FINGERS + 1 and self.cmp_positions(position, self.fingers[min_next_finger][0]) > 0

        # we can't have multiple notes on one string
        if position[STRING] in [p[STRING] for p in existing_positions]:
            return False
        # we also can't have multiple notes on one finger unless the fret is barreable
        if f1 in self.fingers and not (f1 == 1 and max_open_string < top_barre_string):
            return False

        # we can't place an open note beneath an existing barre
        if f1 is None and top_barre_string < position[STRING]:
            return False
        # the new position must place the finger in between the fingers on either side of it
        if passes_prev_finger or passes_next_finger:
            return False
        # the new position cannot place the finger outside its span with other fingers
        for f2 in [f for f in range(NUM_FINGERS) if f in self.fingers]:
            if Fingering.max_finger_distances[f1][f2] < Fingering.distance(position, self.fingers[f2][0]):
                return False

        # we can add the position to the fingering as long as the designated finger isn't being used
        if f1 in self.fingers:
            self.fingers[f1] += [position]
            self.fingers[1].sort()
        else:
            self.fingers[f1] = [position]
        self.stretch_cost = self.__calculate_stretch()

        return True
    
    def get_all_positions(self):
        return [position for finger in self.fingers.values() for position in finger]

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
                finger_stretch += Fingering.distance(self.fingers[f_curr][0],
                                                         self.fingers[f_next][0],
                                                         f_next - f_curr)
                f_curr = f_next

        return finger_stretch

    @classmethod
    def distance(cls, f_1, f_2, modifier=1):
        '''
        Calculation for the Euclidean distance between two fingertips on the fretboard.
        f_1: a tuple representing a finger, in the form (fret_no, string_no)
        f_2: a tuple representing another finger, in the form (fret_no, string_no)
        modifier: a factor representing how much easier this distance should be 
        considered than normal
        Returns: a Decimal value
        '''
        return sqrt((f_2[FRET]*2.5-f_1[FRET]*2.5)**2+(f_2[STRING]-f_1[STRING])**2)/modifier

    def transition(self, other):
        '''
        Calculates the relative difficulty of moving from this fingering to another specified 
        fingering.
        other: a Fingering object representing the chord being moved to
        finger_inactivity: an array representing how long each finger has been in-place
        Returns: a Decimal value
        '''
        finger_movement = 0

        for i in range(NUM_FINGERS):
            if i + 1 in self.fingers and i + 1 in other.fingers:
                curr_finger = self.fingers[i + 1]
                next_finger = other.fingers[i + 1]
                finger_movement += Fingering.distance(curr_finger[0], next_finger[0], 1)
        return finger_movement
