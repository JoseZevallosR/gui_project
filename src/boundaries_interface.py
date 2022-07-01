import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.app import App

from popups_dialog import *

#Importing all the kvs
Builder.load_file('../kv/gwf.kv')
Builder.load_file('../kv/gwfic.kv')
Builder.load_file('../kv/gwfnpf.kv')
Builder.load_file('../kv/gwfrcha.kv')
Builder.load_file('../kv/gwfevta.kv')
Builder.load_file('../kv/gwfdrn.kv')


class gwf_interface(FloatLayout):
	def generate_bc(self):
		print(self.ids['newton_options'].text)
	pass

class gwfic_interface(FloatLayout):
	pass

class gwfnpf_interface(FloatLayout):
	pass

class gwfrcha_interface(FloatLayout):
	pass

class gwfevta_interface(FloatLayout):
	pass

class gwfdrn_interface(FloatLayout):

	def dismiss_popup(self):
		self._popup.dismiss()
	def show_load(self,id_layer):
		self.id_layer_text=id_layer
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content,size_hint=(0.9, 0.9))
		self._popup.open()

	def load(self, path, filename):
		self.ids[self.id_layer_text].text=os.path.join(path, filename[0])
		self.dismiss_popup()


#class MainApp(App):
#	def build(self):		
#		return gwf_interface()



#MainApp().run()