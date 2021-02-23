import mido
import threading
from time import time
from pynput import keyboard

from modules.core.util import *


# This listener also listens to the computer's keyboard and uses user input
# to construct fake midi messages to insert into 'msgseq'. This allows the
# developer to test the program without necessarily having a musical keyboard
# present :-)
class Listener():
    def __init__(self, callback):
        self.callback = callback    # callback with which to send updates
        self.msgseq = []            # sequence of accumulated midi messages
        self.notedt = .05           # time difference to distinguish notes
                                    # and chords
        self.finished = False
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()
        self.keyboard_listener = keyboard.Listener(
                on_release=self.on_key_release)
        self.keyboard_listener.start()
    
    def stop(self):
        self.finished = True
        self.keyboard_listener.stop()
    
    # Convert msgseq to noteseq
    def get_noteseq(self):
        print("msgseq:", self.msgseq, "\n")
        groups = []
        group = []
        for (i, msg) in enumerate(self.msgseq):
            if i != len(self.msgseq) - 1:
                print("dt for msg %d is %f" % (i, self.msgseq[i+1].time - msg.time))
            group.append(msg)
            if i == len(self.msgseq) - 1 or self.msgseq[i+1].time - msg.time > self.notedt:
                groups.append(group)
                group = []
        print("groups:", groups, "\n")
        noteseq = []
        for group in groups:
            if len(group) == 1:
                noteseq.append(group[0].note)
            else:
                noteseq.append([msg.note for msg in group])
        print("noteseq", noteseq, "\n")
        return noteseq
    
    def listen(self):
        try:
            midi_name = mido.get_input_names()[0]
        except IndexError:
            print("Failed to open midi port")
            return
        print("connecting to midi device '%s'" % midi_name)
        midi_in = mido.open_input(midi_name)
        for msg in midi_in:
            if self.finished:
                break
            if msg.type == 'note_on' and msg.velocity != 0:
                newmsg = mido.Message('note_on', note=msg.note,velocity=msg.velocity, time=time())
                self.msgseq.append(newmsg)
                self.callback(self.get_noteseq())
        print("Exercise completed, closing midi port")
        midi_in.close()
    
    key_defs = {
        'q': 60,
        '2': 61, 
        'w': 62,
        '3': 63,
        'e': 64, 
        'r': 65,
        '5': 66,
        't': 67, 
        '6': 68,
        'y': 69,
        '7': 70, 
        'u': 71,
        'i': 72,
        'z': 48,
        's': 49, 
        'x': 50,
        'd': 51,
        'c': 52, 
        'v': 53,
        'g': 54,
        'b': 55, 
        'h': 56,
        'n': 57,
        'j': 58, 
        'm': 59,
        ',': 60,
    }
    def on_key_release(self, key):
        if str(key).strip("''") in Listener.key_defs.keys():
            note = Listener.key_defs[str(key).strip("''")]
            message = mido.Message('note_on', note=note, velocity=50, time=time())
            self.msgseq.append(message)
            self.callback(self.get_noteseq())
























