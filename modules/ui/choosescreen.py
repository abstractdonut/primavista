from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem, IRightBodyTouch
from kivymd.uix.progressbar import MDProgressBar

from modules.ui.eprogressbar import EProgressBar
from modules.core.exerciseinfo import exercise_info

class ChooseScreen(MDScreen):
    
    def on_pre_enter(self):
        self.clear()        # It's necessary to do this every time the exercise
        self.populate()     # list is accessed to keep progresses updated.
    
    def populate(self):
        for exercise_type in exercise_info.keys():
            name = exercise_info[exercise_type][0]
            listitem = ExerciseListItem(text=name)
            listitem.set_progress(exercise_info[exercise_type][2])
            listitem.exercise_type = exercise_type
            listitem.on_release = self.make_goto(listitem)
            self.ids['exerciselist'].add_widget(listitem)
    
    def clear(self):
        lst = self.ids['exerciselist']
        for child in lst.children:
            lst.remove_widget(child)
    
    def make_goto(self, widget):
        return lambda: self.goto_exercise(widget)
    
    def goto_exercise(self, widget):
        self.manager.set_exercise(widget.exercise_type)
        self.manager.goto_exercise()


class ExerciseListItem(OneLineListItem):
    def set_progress(self, value):
        self.ids['progress'].set_progress(value)
























