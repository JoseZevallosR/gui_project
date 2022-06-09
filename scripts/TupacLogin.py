from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


#Define our different screens
class ModelWindow(Screen):
	pass

class MeshWindow(Screen):
	pass

class MenuManager(ScreenManager):
	pass

#Designate our kv
kv = Builder.load_file('managerwindow.kv')



#Window.clearcolor = (1,1,1,1)
Window.size = (400,600)

class loging(Widget):
	pass

class MainApp(App):
	def build(self):
		return kv


MainApp().run()