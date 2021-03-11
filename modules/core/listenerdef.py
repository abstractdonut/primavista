import mido
import threading
from time import time
from pynput import keyboard

# from modules.core.util import *

# Listener maintains the following state.
#
#       'active'            If False then the listener will ignore all input
#                           events.
#       'connected'         True exactly when the listener has a reference to
#                           an open midi port. If True, then a keyboard listener
#                           may also have been started.
#       'device_name'       The name of the midi input device.
#       'midi_port'         The midi port opened using 'device_name'
#       'kb_listener'       The pynput.keyboard.Listener used to capture
#                           keyboard input.
#       'msg_seq'           List of midi messages obtained from user input.
#       'note_seq'          note_seq is not actually part of the state, but
#                           is a list of intermixed notes and chords extracted
#                           from 'msg_seq'. It is necessary to obtain separate
#                           lists from 'msg_seq' and 'note_seq' since whether
#                           or not a note belongs to a chord group can't be
#                           determined in real time.
#       'chord_dt'          midi_on messages which occur within this time
#                           interval will belong to the same chord group.
#       'callbacks'         List of callback functions to send new 'note_seq's
#                           to. There should not be more than one object using 
#                           the listener at once, since one object may clear
#                           the listener. However, if an single object adds its
#                           callback to the listener before previous listeners
#                           are closed, this should not break the program.
#
# The listener also listens to the computer's keyboard and uses user input to
# construct fake midi messages to insert into 'msg_seq'. This allows the
# developer to test the program without necessarily having a musical keyboard
# present :-)
class Listener():
    def __init__(self, use_keyboard=False):
        self.active = False
        self.connected = False
        self.device_name = self.get_first_device()
        self.set_device(self.device_name)
        self.midi_port = None
        self.use_keyboard = use_keyboard
        self.kb_listener = None
        self.msg_seq = []
        self.note_seq = []
        self.chord_dt = .05
        self.callbacks = []
    
    # Open a midi port and start a keyboard listener if appropriate. This must
    # be done before the listener is started.
    def connect(self):
        print("all devices:", self.get_all_devices())
        print("current device:", self.device_name)
        if not self.connected:
            try:
                self.midi_port = mido.open_input(self.device_name)
                self.midi_port.callback = self._on_midi_event
            except IOError:
                raise RuntimeError("listener failed to open midi port.")
                self.device_name = ''
                self.midi_port = None
                return
            if self.use_keyboard:
                self.kb_listener = keyboard.Listener(on_release=self.on_key_release)
                self.kb_listener.start()
            self.connected = True
            print("listener successfully opened midi port.")
            print("device_name is", self.device_name)
    
    # Close the midi port and the keyboard listener if it exists.
    def disconnect(self):
        if self.connected:
            self.midi_port.close()
            if self.use_keyboard:
                self.kb_listener.stop()
            self.connected = False
    
    def is_connected(self):
        return self.connected
    
    # Choose which midi device to listen to. If already connected to a device,
    # this operation will cause the device to be closed, and the new device to
    # be opened. If not already connected to a device, then this operation
    # does not connect to the new device.
    def set_device(self, device_name):
        try:
            self.device_name = device_name
            if self.connected:
                self.disconnect()
                self.connect()
        except RuntimeError:
            print("Failed to connect listener.")
            self.device_name = ''
            self.midi_port = None
    
    # Return the name of the currently opened device.
    def get_device(self):
        return self.device_name
    
    # Return a list of the names of all devices which the listener may open.
    def get_all_devices(self):
        return mido.get_input_names()
    
    # The name of the default device used by primavista. The user may choose
    # another device from the DeviceScreen.
    def get_first_device(self):
        names = self.get_all_devices()
        return names[0] if len(names) > 0 else ''
    
    # Whenever new user input is detected, it will be processed and the
    # resulting note_seq sent to each callback added to the listener.
    def add_callback(self, callback):
        self.callbacks.append(callback)
    
    # When an object no longer needs to receive updates from the listener, it
    # should remove its callback.
    def remove_callback(self, callback):
        print("current listener callbacks", self.callbacks)
        self.callbacks.remove(callback)
    
    # If an object expect to be the only user of the listener, it can simply
    # remove any callbacks currently registered with the listener. 
    def remove_all_callbacks(self):
        self.callbacks = []
    
    # Start listening for user input, sending the results to any registered
    # callbacks.
    def start(self):
        if not self.connected:
            raise RuntimeError("listener must be connected before it is started.")
        self.active = True
    
    # Pause listening for user input, but do not remove messages that the
    # listener has already accumulated.
    def pause(self):
        self.active = False
    
    # Stop listening for user input, and remove any messages that the listener
    # has already accumulated.
    def stop(self):
        self.active = False
        self.clear()
    
    # Remove any messages that the listener has accumulated.
    def clear(self):
        self.msg_seq = []
    
    # Process accumulated messages and return a list of notes and chords.
    def get_note_seq(self):
        groups = []
        group = []
        for (i, msg) in enumerate(self.msg_seq):
            group.append(msg)
            if i != len(self.msg_seq) - 1:
                print("type(msg_seq[i+1]) =", type(self.msg_seq[i+1]))
            print("type(msg) =", type(msg))
            print("type(self.chord_dt) =", type(self.chord_dt))
            if i == len(self.msg_seq) - 1 or \
               self.msg_seq[i+1].time - msg.time > self.chord_dt:
                groups.append(group)
                group = []
        note_seq = []
        for group in groups:
            if len(group) == 1:
                note_seq.append(group[0].note)
            else:
                note_seq.append([msg.note for msg in group])
        return note_seq
    
    # Record a new message. Internal method used by _on_midi_event and
    # _on_key_release.
    def _add_msg(self, msg):
        self.msg_seq.append(msg)
        note_seq = self.get_note_seq()
        for callback in self.callbacks:
            callback(note_seq)
    
    # Capture a midi event and, if it's a "midi_on" event, record it.
    def _on_midi_event(self, msg):
        if self.active and msg.type == 'note_on' and msg.velocity != 0:
            print("listener received midi event:", msg)
            newmsg = mido.Message('note_on', note=msg.note,velocity=msg.velocity, time=time())
            self._add_msg(newmsg)
    
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
    # Capture keyboard input and interpret it as a midi message and record it if
    # it is a key in the above dictionary.
    def _on_key_release(self, key):
        if self.active and str(key).strip("''") in Listener.key_defs.keys():
            note = Listener.key_defs[str(key).strip("''")]
            message = mido.Message('note_on', note=note, velocity=50, time=time())
            self._add_msg(message)


















