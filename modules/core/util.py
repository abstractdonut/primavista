import mingus.core.notes as notes

# consider renaming 'str_to_midinum'
def note_to_midinum(note):
    letter, number = note.split('-')
    return notes.note_to_int(letter.upper()) + 12 * int(number) + 12

# consider renaming 'midinum_to_str'
def midinum_to_note(n):
    letter = n % 12
    number = n // 12 - 1
    return notes.int_to_note(letter) + '-' + str(number)

def enum_notes(letter):
    base = notes.note_to_int(letter.upper())
    return [base + i for i in range(0, 128, 12)]

def isclef(clef):
    return clef in ["treble", "alto", "tenor", "bass", "baritone"]


## test me
#for i in range(21, 50):
#    note = midinum_to_note(i)
#    midinum = note_to_midinum(note)
#    print("%d\t%s\t%d" % (i, note, midinum))
