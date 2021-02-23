from kivymd.uix.screen import MDScreen


class MasteredScreen(MDScreen):
    def next_exercise(self):
        self.manager.set_exercise()
        self.manager.goto_exercise()
    
    def continue_exercise(self):
        self.manager.goto_exercise()
    
    def choose_exercise(self):
        self.manager.goto_choose()
