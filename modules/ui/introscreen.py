from kivymd.uix.screen import MDScreen


class IntroScreen(MDScreen):
    def goto_exercise(self):
        self.manager.goto_exercise()
        print("IntroScreen: goto_exercise")
    
    def goto_choose(self):
        self.manager.goto_choose()
