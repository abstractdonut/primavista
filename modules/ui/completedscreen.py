from kivymd.uix.screen import MDScreen
from kivy.clock import Clock

from modules.core.exerciseinfo import exercise_info

class CompletedScreen(MDScreen):
    
    def on_enter(self):
        pass
        #Clock.schedule_once(self.goto_exercise, 1)
    
    def set_exercise_values(self, progress, timediff, mistakes):
        self.ids['progress'].text = "You earned %.2f progress points" % progress
        self.ids['mistakes'].text = str(mistakes)
        self.ids['time'].text = "%.2f seconds" % timediff
    
    def goto_exercise(self, dt):
        self.manager.goto_exercise()
