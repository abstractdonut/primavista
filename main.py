from kivy.core.window import Window
Window.maximize()
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock

from modules.ui.introscreen import IntroScreen
from modules.ui.choosescreen import ChooseScreen
from modules.ui.exercisescreen import ExerciseScreen
from modules.ui.completedscreen import CompletedScreen
from modules.ui.masteredscreen import MasteredScreen
from modules.core.exerciseinfo import *

import mido
import threading

from os.path import isfile, join, isdir
from kivy.lang import Builder
from kivy.resources import resource_add_path

import os, sys
sys.path.append(os.getcwd())

kv_path = os.getcwd() + '/layouts/'
kv_load_list = [
#    "primavista.kv",
    "eprogressbar.kv",
    "introscreen.kv",
    "choosescreen.kv",
    "exercisescreen.kv",
    "completedscreen.kv",
    "masteredscreen.kv"
]

resource_add_path(kv_path)

for _file in kv_load_list:
        print("Attempting to load following path:")
        print(kv_path + _file, "\n")
        Builder.load_file(_file)


class PrimaVistaUI(ScreenManager):
    def __init__(self, **kwargs):
        super(PrimaVistaUI, self).__init__(**kwargs)
        self.introscreen = IntroScreen(name="intro")
        self.choosescreen = ChooseScreen(name="choose")
        self.exercisescreen = ExerciseScreen(name="exercise")
        self.completedscreen = CompletedScreen(name="completed")
        self.masteredscreen = MasteredScreen(name="mastered")
        self.add_widget(self.introscreen)
        self.add_widget(self.choosescreen)
        self.add_widget(self.exercisescreen)
        self.add_widget(self.completedscreen)
        self.add_widget(self.masteredscreen)
        self.current = "intro"
        Window.bind(on_keyboard=self.on_key)
        self.hold = False   # see self.start_hold for explanation
    
    # See https://gist.github.com/Enteleform/a2e4daf9c302518bf31fcc2b35da4661
    # for all key codes.
    def on_key(self, window, key, *args):
        if self.hold:
            return True
        self.start_hold()
        if key == 27:   # escape
            self.escape()
        if key == 46:   # period
            self.goto_completed()
        if key == 47:   # forward slash
            self.goto_mastered()
        return True
    
    # For whatever reason buttons sometimes release twice following a single
    # press. The hold prevents this function from being called twice within
    # some span of time.
    def start_hold(self):
        self.hold = True
        Clock.schedule_once(self.end_hold, 0.1)
    
    def end_hold(self, dt):
        self.hold = False
    
    def escape(self):
        if self.current == "intro":
            MDApp.get_running_app().stop()
        elif self.current == "exercise" or self.current == "choose":
            self.goto_intro()
        else:
            self.goto_exercise()
    
    def set_exercise(self, exercise=None):
        self.exercisescreen.new_exercise(exercise)
    
    def goto_intro(self):
        self.exercisescreen.skip_exercise()
        self.transition.direction = "right"
        self.current = "intro"
    
    def goto_choose(self):
        print("goto_choose")
        if self.current == "intro":
            self.transition.direction = "left"
        else:
            self.transition.direction = "right"
        self.current = "choose"
    
    def goto_exercise(self):
        print("goto_exercise")
        self.transition.direction = "left"
        self.current = "exercise"
    
    def goto_completed(self, progress=0, timediff=0, mistakes=0):
        print("goto_completed")
        self.completedscreen.set_exercise_values(progress, timediff, mistakes)
        self.transition.direction = "left"
        self.current = "completed"
    
    def goto_mastered(self):
        print("goto_mastered")
        self.transition.direction = "left"
        self.current = "mastered"


class PrimaVistaApp(MDApp):
    def build(self):
        return PrimaVistaUI()
    
    def on_stop(self):
        save_exercise_info()


if __name__ == '__main__':
    PrimaVistaApp().run()







































