from modules.core.exercise import *

import pickle
import os


# Here is a list of every sight reading exercise and its corresponding name and instructions

def save_exercise_info():
    with open("data/progress.pickle", 'w+b') as handle:
        pickle.dump(exercise_info, handle)

def load_exercise_info():
    try:
        with open("data/progress.pickle", 'rb') as handle:
            return pickle.load(handle)
    except FileNotFoundError:
        return {
            Exercise1A: ["Key Signatures I", "Play the root note of the given major key.", 0],
            Exercise1B: ["Key Signatures II", "Play the root note of the given major key.", 0],
            Exercise1C: ["Key Signatures III", "Play the root note of the given minor key.", 0],
            Exercise1D: ["Key Signatures IV", "Play the root note of the given minor key.", 0],
            Exercise2A: ["C major - right hand", "Play the given note.", 0],
            Exercise2B: ["C major - left hand", "Play the given note.", 0],
            Exercise3A: ["Perfect fifths - right hand", "Play the given interval.", 0],
            Exercise3B: ["Perfect fifths - left hand", "Play the given interval.", 0],
            Exercise4A: ["Pentascales - right hand", "Play the pentascale for the given key.", 0],
            Exercise4B: ["Pentascales - left hand", "Play the pentascale for the given key.", 0]
        }


# exercise class, name, and instructions
exercise_info = load_exercise_info()
