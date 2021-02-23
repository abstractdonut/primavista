
from random import choice, randrange

from modules.core.util import *

class NoteSet():
    # It is recommended that mingus is used to create scales and chords which
    # can be inserted into a notes list and added as an argument to this
    # initializer. 'notes' may be any mixture of string specific format ("C-4"),
    # string group format ("C"), or integer midi note number (60). clefs must be
    # one of "treble", "bass", "alto", "tenor", and "baritone". 'random' is True
    # will cause the previous arguments to be ignored and instead, a random set
    # of n notes within the givin bounds will produced. If 'random' is False
    # then 'n' has no effect. 'bounds' are honored regardless of the value of
    # 'random'. 'bounds' are inclusive. Alternatively, notes can be constrained
    # by whether or not the fall into the set of notes obtained from 'inclef'.
    # In essense, inclef is simply an alternative way of determining bounds for
    # the NoteSet.
    def __init__(self, notes=[],  clefs=[], random=False, n=12, bounds=["A-0", "G-9"], inclef=None):
        self.notes = []     # midi note numbers
        for note in notes:
            self.notes += NoteSet.to_midinum(note)
        for clef in clefs:
            self.notes += NoteSet.get_clef(clef)
        #print("obtained following notes before clipping", self.notes)
        l, u = NoteSet.get_bounds(bounds, inclef)   
        #print("obtained bounds %d and %d for self.notes" % (l, u))
        if random:
            self.notes = []
            while len(self.notes) < n:
                self.notes.append(randrange(l, u + 1))
        self.notes = NoteSet.clip(self.notes, l, u)
        self.notes.sort()
        #print("after clipping", self.notes)
    
    def __repr__(self):
        return str([midinum_to_note(note) for note in self.notes])
    
    @staticmethod
    def get_bounds(bounds, clef):
        extra = NoteSet.get_clef(clef)
        if extra:
            c_l = min(extra)
            c_u = max(extra)
            l = max(c_l, NoteSet.to_midinum(bounds[0])[0])
            u = min(c_u, NoteSet.to_midinum(bounds[1])[0])
        else:
            l = NoteSet.to_midinum(bounds[0])[0]
            u = NoteSet.to_midinum(bounds[1])[0]
        return l, u
    
    # Remove all entries from numlist that don't fall into the in   clusive range
    # [l, u].
    @staticmethod
    def clip(numlist, l, u):
        new = []
        for num in numlist:
            if l <= num <= u:
                new.append(num)
        return new
    
    # This is distinct from the utilities
    @staticmethod
    def to_midinum(note):
        if type(note) == int:
            return [note]
        elif type(note) == str and '-' in note:
            return [note_to_midinum(note)]
        elif type(note) == str and not '-' in note:
            return enum_notes(note)
        return []
    
    # Obtain the set of notes which extend across a given clef. clef must be one
    # of "treble", "bass", "alto", "tenor", or "baritone".
    @staticmethod
    def get_clef(clef):
        if clef == "treble":
            return list(range(60, 82))       # treble = c4 to a5
        elif clef == "bass":
            return list(range(40, 61))       # bass = e2 to c4
        elif clef == "alto":
            return list(range(50, 72))       # alto = d3 to b4
        elif clef == "tenor":
            return list(range(47, 68))       # tenor = b2 to g4
        elif clef == "baritone":
            return list(range(43, 65))       # baritone g2 to e4
        return []
    
    ####
    # All the methods above are class helpers. All the methods below are
    # intended for usage by the user.
    ####
    
    # Select a random note from the NoteSet.
    def random(self):
        return choice(self.notes)
    
    # Obtain the nearest note above the given note.
    def next(self, note, step=1):
        note = NoteSet.to_midinum(note)[0]
        i = self.notes.index(note)
        i = (i + step) % len(self.notes)
        return self.notes[i]
    
    # Obtain the nearest note below the given note.
    def prev(self, note, step=1):
        note = NoteSet.to_midinum(note)[0]
        i = self.notes.index(note)
        i = (i - step) % len(self.notes)
        return self.notes[i]
    
    # Determine if the given note is the highest one.
    def islast(self, note):
        note = NoteSet.to_midinum(note)[0]
        i = self.notes.index(note)
        return i == len(self.notes) - 1
    
    # Determine if the given note is the lowest one.
    def isfirst(self, note):
        note = NoteSet.to_midinum(note)[0]
        i = self.notes.index(note)
        return i == 0
    
    # Obtain the nearest note to a given note. 'tie' may be "next" or "prev".
    def nearest(self, note, tie="next"):
        note = NoteSet.to_midinum(note)[0]
        next = self.next(note)
        prev = self.prev(note)
        if next - note < note - prev:
            return next
        elif note - prev < next - note:
            return prev
        elif tie == "next":
            return next
        return prev
    
    # Remove all entries in self.notes which come before the first instance of
    # 'note' in self.notes.
    def shave_before(self, note):
        note = min(NoteSet.to_midinum(note)) % 12
        while True:
            if len(self.notes) == 0:
                break
            if self.notes[0] % 12 == note:
                break
            del self.notes[0]
    
    # Remove all entries in self.notes which come after the last instance of
    # 'note' in self.notes.
    def shave_after(self, note):
        note = max(NoteSet.to_midinum(note)) % 12
        while True:
            if len(self.notes) == 0:
                break
            if self.notes[-1] % 12 == note:
                break
            del self.notes[-1]
























