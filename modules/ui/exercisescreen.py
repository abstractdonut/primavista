from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

from modules.core.exerciseinfo import *
from modules.ui.eprogressbar import EProgressBar

import mido
import threading


class ExerciseScreen(MDScreen):
    def __init__(self, **kwargs):
        super(ExerciseScreen, self).__init__(**kwargs)
        self.exercise = None
    
    def on_pre_enter(self):
        #print("ExerciseScreen: on_pre_enter")
        if self.exercise is None:
            self.new_exercise()
    
    def on_enter(self):
        self.exercise.start()
    
    def on_exercise_complete(self):
        self.exercise.stop()
        progress_inc = type(self).calc_progress(*self.exercise.performance())
        exercise_info[type(self.exercise)][2] += progress_inc
        new_progress = exercise_info[type(self.exercise)][2]
        old_progress = self.get_progress()
        self.set_progress(new_progress)
        if old_progress < 100 and new_progress >= 100:
            self.manager.goto_mastered()
        else:
            #print("on_exercise_complete, preparing to goto_completed")
            timediff, mistakes = self.exercise.performance()
            self.manager.goto_completed(progress_inc, timediff, mistakes)
        # The listener needs a chance to close the midi port before a new one
        # is opened in new_exercise.
        _new_exercise = lambda dt: self.new_exercise(type(self.exercise))
        Clock.schedule_once(_new_exercise, .05)
    
    def new_exercise(self, exercise_type=None):
        #print("ExerciseScreen: new_exercise", exercise_type)
        if exercise_type is None:
            exercise_type = self.get_unmastered_exercise()
        if not self.exercise is None:
            #print("Stoping completed exercise")
            self.exercise.stop()
        name, instr, progress = exercise_info[exercise_type]
        self.ids['name'].text = name
        self.ids['instructions'].text = instr
        self.set_progress(progress)
        self.exercise = exercise_type(self.on_exercise_complete)
        
        self.exercise.make_png(self.make_png_callback)
        self.played_notes = []
    
    def make_png_callback(self):
        self.reload()

    def skip_exercise(self):
        self.new_exercise(type(self.exercise))
        self.exercise.start()
    
    def get_unmastered_exercise(self):
        return list(exercise_info)[0]
    
    # This is an internal functino used to set the value of the progress bar
    # contained in the ExerciseScreen. It does not change the actual value
    # of the exercise's progress.
    def set_progress(self, value):
        self.ids['progress'].set_progress(value)
    
    def get_progress(self):
        return self.ids['progress'].get_progress()
    
    # If the exercise is completed in under three seconds and with zero
    # mistakes, the user obtains 6 progress points. Every additional three
    # seconds, and every additional mistake, each divide the progress points
    # earned by 2. For instance, if the user makes takes 6 seconds to complete
    # an exercise and makes one mistake, he obtaines 1.5 progress points.
    # After the user obtaines 100 progress points, he has mastered the
    # exercise. The idea is that a user should master the exercise after
    # not much more than 20 reasonable attempts.
    @staticmethod
    def calc_progress(timediff, mistakes):
        mpenalty = 2 ** (-mistakes)
        tpenalty = 2 ** ( (3 - timediff) / 3 ) if timediff >= 3 else 1
        return 6 * mpenalty * tpenalty
    
    # It is necessary to schedule the reload so that there is time for lilypond
    # to generate the next png. Otherwise, 'Image.reload' simply loads a blank
    # image.
    def reload(self):
        Clock.schedule_once(self._reload, .1)
    
    # The exercise is started here instead of in 'set_exercise' because 
    # this functions execution is the most recent thing known to happen before
    # the exercise score is displayed to the user. 
    def _reload(self, dt):
        self.ids['score'].reload()
    
    def goto_choose(self):
        self.manager.goto_choose()























