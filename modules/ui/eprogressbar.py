from kivymd.uix.gridlayout import MDGridLayout

# Exercise Progress Bar
class EProgressBar(MDGridLayout):
    def set_progress(self, value):
        red = 1 - min(value, 100) / 100
        self.ids['progress'].color = (red, 1, 0, 1)
        self.ids['progress'].value = value
        self.ids['percent'].text = "%d%%" % value
    
    def get_progress(self):
        return self.ids['progress'].value
