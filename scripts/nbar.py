from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
# load and save dialog
class LoadDialog(Widget):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


tupackv = Builder.load_file('tupacbar.kv')

class TupacMaster(BoxLayout):

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
		self.ids.limit_layer.text=os.path.join(path, filename[0])
		print(self.ids)		
		self.dismiss_popup()


class MainApp(MDApp):
	def build(self):
		self.theme_cls.theme_style = 'Dark'
		self.theme_cls.primary_palette = 'BlueGray'
		return TupacMaster()


MainApp().run()