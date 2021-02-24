import mingus.core.notes as notes
import mingus.core.keys as keys
import mingus.core.scales as scales
from mingus.containers import Bar
from mingus.containers.track import Track
from mingus.containers.composition import Composition
from mingus.extra.lilypond import *

from modules.core.util import *
from modules.core.listener import *
from modules.core.noteset import *

from PIL import Image

from random import randint, choice, choices
from time import time
import threading


class ExerciseBase():
    # Here is a sample exercise. To create a new exercise, override __init__.
    # __init__ must define the same fields in every derived class.
    # (callback, listener, userseq, targetseq, clef, and key)
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.targetseq = [52, 54, 56, 57, 59]
        self.clef = "bass"
        self.key = 4
    
    def start(self):
        self.starttime = time()
        self.finished = False
    
    def stop(self):
        if not hasattr(self, 'finished'):
            self.finished = False
        if not self.finished:
            self.stoptime = time()
            self.listener.stop()
            self.finished = True
    
    def listener_callback(self, noteseq):
        self.userseq = noteseq
        complete = self.check()
        if complete:
            self.callback()
    
    # Take a sequence of midi note numbers, presumably obtained through a midi
    # input port, and check if the midi note numbers contain the notes in the
    # exercise.
    def check(self):
        return type(self).contains(self.userseq, self.targetseq)
    
    # return a tuple (time, mistakes) where time is the time in seconds in which
    # the exercise was complete, and mistakes counts the number of notes in
    # userseq which did not contribute to completing the exercise.
    def performance(self):
        if self.finished:
            timediff = self.stoptime - self.starttime
            mistakes = len(self.userseq) - len(self.targetseq)
            return (timediff, mistakes)
        else:
            raise RuntimeError("Exercise.performance cannot calculate performance before exercise is finished.")
    
    # https://stackoverflow.com/questions/3847386/how-to-test-if-a-list-contains-another-list
    @staticmethod
    def contains(big, small):
        for item in big:
            if type(item) == list or type(item) == tuple:
                item.sort()
        for item in small:
            if type(item) == list or type(item) == tuple:
                item.sort()
        for i in range(len(big)-len(small)+1):
            for j in range(len(small)):
                if big[i+j] != small[j]:
                    break
            else:
                return True
        return False
    
    # Convert the exercise into a user readable png with the given filename.
    def make_png(self, callback, filename="images/exercise"):
        args = (callback, filename,)
        thread = threading.Thread(target=self.make_png_thread, args=args, daemon=True)
        thread.start()
    
    def make_png_thread(self, callback, filename):
        type(self).exec_lilypond(self.make_ly(), filename, "-fpng")
        type(self).adjust_width()
        callback()
    
    def make_ly(self):
        header = """\paper{
            page-breaking = #ly:one-line-breaking
            paper-width=100\mm
            paper-height=20\mm
            left-margin=2\mm
            right-margin=2\mm
            top-margin=2\mm
            bottom-margin=2\mm
            oddFooterMarkup=##f
            oddHeaderMarkup=##f
            bookTitleMarkup = ##f
            scoreTitleMarkup = ##f\n}\n\n"""
        clef = "\\clef " + self.clef + " "
        key = self.get_key()
        notes = self.get_notes()
        print("{ " + key + clef + notes + "}")
        return header + "{ " + key + clef + "{ " + notes + "}" + " }"
    
    def get_key(self):
        note = notes.int_to_note(self.key)
        note = note.replace('#', 'is').replace('b', 'es').lower()
        return "\\key %s \\major " % note
    
    ly_octaves = {
        0: ",,,",
        1: ",,",
        2: ",",
        3: "",
        4: "\'",
        5: "\'\'",
        6: "\'\'\'",
        7: "\'\'\'\'",
        8: "\'\'\'\'\'",
        9: "\'\'\'\'\'\'",
        10: "\'\'\'\'\'\'\'"
    }
    def get_notes(self):
        notes = []
        print("get_notes: self.targetseq =", self.targetseq)
        for item in self.targetseq:
            if type(item) == list or type(item) == tuple:
                notes.append("<")
                for midinum in item:
                    notes.append(self.midinum_to_ly(midinum))
                notes.append(">")
            else:
                notes.append(self.midinum_to_ly(item))
        return " ".join(notes) + " "
    
    # Converts a midi note number to a lilypond style note.
    def midinum_to_ly(self, midinum):
        note, octave = midinum_to_note(midinum).split('-')
        note = note.replace('#', 'is').replace('b', 'es').lower()
        octave = type(self).ly_octaves[int(octave)]
        return note + octave
    
    # Modified version of
    # mingus.extra.lilypond.Exercise.save_string_and_execute_LilyPond
    # This is necessary to increase the resolution of the generated png.
    @staticmethod
    def exec_lilypond(ly_string, filename, command):
        """A helper function for to_png and to_pdf. Should not be used directly."""
        ly_string = '\\version "2.10.33"\n' + ly_string
        if filename[-4:] in [".pdf", ".png"]:
            filename = filename[:-4]
        try:
            f = open(filename + ".ly", "w")
            f.write(ly_string)
            f.close()
        except:
            return False
        command = 'lilypond %s -dresolution=600 -o "%s" "%s.ly"' % (command, filename, filename)
        print("Executing: %s" % command)
        p = subprocess.Popen(command, shell=True).wait()
        os.remove(filename + ".ly")
        return True
    
    @staticmethod
    def adjust_width(filename="images/exercise.png"):
        im = Image.open(filename)
        width = im.width
        new_width = 3400
        height = im.height
        result = Image.new(im.mode, (new_width, height), (255, 255, 255))
        result.paste(im, ((new_width - width) // 2, 0))
        result.save(filename)
    
    # Generate a random single note.
    def gen_single_note(self, noteset=None):
        if noteset is None:
            noteset = self.dn
        return noteset.random()
    
    # Generate 'n' random adjacent notes starting with root. 'weights' determine
    # the probability that a sucessive note is lower than, equal to, or higher
    # than the previous note, and must be a list of the form [p, q, r] for
    # integers p, q, and r.
    def gen_brownian(self, root, n, step, noteset=None, weights=[.25, .15, .6]):
        if noteset is None:
            noteset = self.dn
        res = [root]
        while len(res) < n:
            direction = choices([-1, 0, 1], weights=weights)[0]
            if direction == 1:
                res.append(noteset.next(res[-1], step=step))
            elif direction == -1:
                res.append(noteset.prev(res[-1], step=step))
            else:
                res.append(res[-1])
        return res
    
    # Choose a random major triad of the given key, whose root falls on the
    # given clef.
    # Key must be a valid uppercase (major) or lowercase (minor) letter
    # corresponding to a diatonic scale.
    # clef must be one of 'treble', 'alto', 'tenor', 'bass', 'baritone'.
    def gen_major_chord(self, key, clef=None):
        tonic = keys.get_key_signature(key)     # tonic of the major scale
        subdom = notes.int_to_note((tonic + 5) % 12)
        dom = notes.int_to_note((tonic + 7) % 12)
        tonic = notes.int_to_note(tonic)
        noteset = NoteSet(notes=[tonic, subdom, dom], inclef=clef)
        print(noteset)
        root = noteset.random()
        return [root, root + 4, root + 7]
        
    # Choose a random minor triad of the given key, whose root falls on the
    # given clef.
    # Key must be a valid uppercase (major) or lowercase (minor) letter
    # corresponding to a diatonic scale.
    # clef must be one of 'treble', 'alto', 'tenor', 'bass', 'baritone'.
    def gen_minor_chord(self, key, clef=None):
        tonic = keys.get_key_signature(key)     # tonic of the major scale
        supton = notes.int_to_note((tonic + 2) % 12)
        mediant = notes.int_to_note((tonic + 4) % 12)
        submed = notes.int_to_note((tonic - 3) % 12)
        noteset = NoteSet(notes=[supton, mediant, submed], inclef=clef)
        root = noteset.random()
        return [root, root + 3, root + 7]
    
    # mode must be one of the scales found in mingus.core.scales listed below.
    # flef must be one of 'treble', 'alto', 'tenor', 'bass', 'baritone'.
    scales = {
        #"diatonic": scales.diatonic,   # bug in mingus, use 'ionian' or 'natural_minor'
        "ionian": scales.Ionian,
        "dorian": scales.Dorian,
        "phrygian": scales.Phrygian,
        "lydian": scales.Lydian,
        "mixolydian": scales.Mixolydian,
        "aeolian": scales.Aeolian,
        "locrian": scales.Locrian,
        "major": scales.Major,
        "harmonic_major": scales.HarmonicMajor,
        "natural_minor": scales.NaturalMinor,
        "harmonic_minor": scales.HarmonicMinor,
        "melodic_minor": scales.MelodicMinor,
        "bachian": scales.Bachian,
        "minor_neapolitan": scales.MinorNeapolitan,
        "chromatic": scales.Chromatic,
        "whole_tone": scales.WholeTone,
        "octatonic": scales.Octatonic
    }
    def gen_scale(self, scale, clef, direction="ascending"):
        scaleclass = ExerciseBase.scales[scale]
        root = notes.int_to_note(randint(0, 11))
        seed = scaleclass(root).ascending()[:-1]
        noteset = NoteSet(notes=seed, inclef=clef)
        noteset.shave_before(root)
        noteset.shave_after(root)
        if direction == "descending":
            noteset.sort(reverse=True)
        return noteset.notes
    
    def gen_arpeggio(self, chord):
        pass

class Exercise1A(ExerciseBase):
    key_choices = [
        ("bis", 0),
        ("c", 0),
        ("cis", 1),
        ("des", 1),
        ("d", 2),
        ("dis", 3),
        ("ees", 3),
        ("e", 4),
        ("fes", 4),
        ("eis", 5),
        ("f", 5),
        ("fis", 6),
        ("ges", 6),
        ("g", 7),
        ("gis", 8),
        ("aes", 8),
        ("a", 9),
        ("ais", 10),
        ("bes", 10),
        ("b", 11),
        ("ces", 11)
    ]
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.targetseq = []
        self.clef = "treble"
        self.lykey, self.key = choice(type(self).key_choices)
    
    def listener_callback(self, noteseq):
        self.userseq = [note % 12 for note in noteseq]
        complete = self.check()
        if complete:
            self.callback()
    
    def check(self):
        return self.key in self.userseq
   
    def performance(self):
        if self.finished:
            timediff = self.stoptime - self.starttime
            mistakes = len(self.userseq) - 1
            return (timediff, mistakes)
    
    def get_key(self):
        return "\\key %s \\major " % self.lykey


class Exercise1B(ExerciseBase):
    key_choices = [
        ("bis", 0),
        ("c", 0),
        ("cis", 1),
        ("des", 1),
        ("d", 2),
        ("dis", 3),
        ("ees", 3),
        ("e", 4),
        ("fes", 4),
        ("eis", 5),
        ("f", 5),
        ("fis", 6),
        ("ges", 6),
        ("g", 7),
        ("gis", 8),
        ("aes", 8),
        ("a", 9),
        ("ais", 10),
        ("bes", 10),
        ("b", 11),
        ("ces", 11)
    ]
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.targetseq = []
        self.clef = "bass"
        self.lykey, self.key = choice(type(self).key_choices)
    
    def listener_callback(self, noteseq):
        self.userseq = [note % 12 for note in noteseq]
        complete = self.check()
        if complete:
            self.callback()
    
    def check(self):
        return self.key in self.userseq
   
    def performance(self):
        if self.finished:
            timediff = self.stoptime - self.starttime
            mistakes = len(self.userseq) - 1
            return (timediff, mistakes)
    
    def get_key(self):
        return "\\key %s \\major " % self.lykey


class Exercise1C(ExerciseBase):
    key_choices = [
        ("bis", 0),
        ("c", 0),
        ("cis", 1),
        ("des", 1),
        ("d", 2),
        ("dis", 3),
        ("ees", 3),
        ("e", 4),
        ("fes", 4),
        ("eis", 5),
        ("f", 5),
        ("fis", 6),
        ("ges", 6),
        ("g", 7),
        ("gis", 8),
        ("aes", 8),
        ("a", 9),
        ("ais", 10),
        ("bes", 10),
        ("b", 11),
        ("ces", 11)
    ]
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.targetseq = []
        self.clef = "treble"
        self.lykey, self.key = choice(type(self).key_choices)
    
    def listener_callback(self, noteseq):
        self.userseq = [note % 12 for note in noteseq]
        complete = self.check()
        if complete:
            self.callback()
    
    def check(self):
        return self.key in self.userseq
   
    def performance(self):
        if self.finished:
            timediff = self.stoptime - self.starttime
            mistakes = len(self.userseq) - 1
            return (timediff, mistakes)
    
    def get_key(self):
        return "\\key %s \\minor " % self.lykey


class Exercise1D(ExerciseBase):
    key_choices = [
        ("bis", 0),
        ("c", 0),
        ("cis", 1),
        ("des", 1),
        ("d", 2),
        ("dis", 3),
        ("ees", 3),
        ("e", 4),
        ("fes", 4),
        ("eis", 5),
        ("f", 5),
        ("fis", 6),
        ("ges", 6),
        ("g", 7),
        ("gis", 8),
        ("aes", 8),
        ("a", 9),
        ("ais", 10),
        ("bes", 10),
        ("b", 11),
        ("ces", 11)
    ]
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.targetseq = []
        self.clef = "bass"
        self.lykey, self.key = choice(type(self).key_choices)
    
    def listener_callback(self, noteseq):
        self.userseq = [note % 12 for note in noteseq]
        complete = self.check()
        if complete:
            self.callback()
    
    def check(self):
        return self.key in self.userseq
   
    def performance(self):
        if self.finished:
            timediff = self.stoptime - self.starttime
            mistakes = len(self.userseq) - 1
            return (timediff, mistakes)
    
    def get_key(self):
        return "\\key %s \\minor " % self.lykey

class Exercise2A(ExerciseBase): 
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        tones = scales.Ionian("C").ascending()[0:7]
        noteset = NoteSet(notes=tones, inclef="treble")
        print("noteset:", noteset)
        self.targetseq = [noteset.random()]
        self.clef = "treble"
        self.key = 0

class Exercise2B(ExerciseBase): 
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        tones = scales.Ionian("C").ascending()[0:7]
        noteset = NoteSet(notes=tones, inclef="bass")
        print("noteset:", noteset)
        self.targetseq = [noteset.random()]
        self.clef = "bass"
        self.key = 0

class Exercise3A(ExerciseBase): 
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        tones = scales.Ionian("C").ascending()[0:7]
        noteset = NoteSet(notes=tones, inclef="treble")
        print("noteset:", noteset)
        root = noteset.random()
        self.targetseq = [[root, root + 7]]
        self.clef = "treble"
        self.key = 0

class Exercise3B(ExerciseBase): 
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        tones = scales.Ionian("C").ascending()[0:7]
        noteset = NoteSet(notes=tones, inclef="bass")
        print("noteset:", noteset)
        root = noteset.random()
        self.targetseq = [[root, root + 7]]
        self.clef = "bass"
        self.key = 0

class Exercise4A(ExerciseBase):
    key_choices = [
        ("c", 0),
        ("d", 2),
        ("e", 4),
        ("f", 5),
        ("g", 7),
        ("a", 9),
        ("b", 11)
    ]
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.clef = "treble"
        self.lykey, self.key = choice(type(self).key_choices)
        key = notes.int_to_note(self.key)
        noteset = NoteSet(notes=[self.lykey.upper()], inclef="treble")
        root = noteset.random()
        self.targetseq = [root, root + 2, root + 4, root + 5, root + 7]

class Exercise4B(ExerciseBase):
    key_choices = [
        ("c", 0),
        ("d", 2),
        ("e", 4),
        ("f", 5),
        ("g", 7),
        ("a", 9),
        ("b", 11)
    ]
    def __init__(self, callback):
        self.callback = callback
        self.listener = Listener(self.listener_callback)
        self.userseq = []
        self.clef = "bass"
        self.lykey, self.key = choice(type(self).key_choices)
        noteset = NoteSet(notes=[self.lykey.upper()], inclef="bass")
        root = noteset.random()
        self.targetseq = [root, root + 2, root + 4, root + 5, root + 7]













