from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window


# load and save dialog
class LoadDialog(Widget):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(Widget):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


#Define our different screens
class ModelWindow(Screen):
	pass

class MeshWindow(Screen):
	loadfile = ObjectProperty(None)
	savefile = ObjectProperty(None)
	text_input = ObjectProperty(None)

	def dismiss_popup(self):
		self._popup.dismiss()
	def show_load(self):
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content,size_hint=(0.9, 0.9))
		self._popup.open()

	def load(self, path, filename):
		with open(os.path.join(path, filename[0])) as stream:
			self.text_input.text = stream.read()
		self.dismiss_popup()

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