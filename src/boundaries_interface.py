import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

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
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.lay_out=FloatLayout(size_hint=(1,0.5))

		
	def add_layers(self,value,*args):
		#lay_out=BoxLayout(orientation='vertical',size_hint=(1,0.5))
		 
		for i in range(int(value)):
			lbl= Label(text=f'K {i+1}',size_hint=(0.2,0.01),pos_hint={'x':0.05,'y':0.98-i*0.01})
			txtI = TextInput(size_hint=(0.2,0.01),pos_hint={'x':0.3,'y':0.98-i*0.01})
			self.lay_out.add_widget(txtI)
			self.lay_out.add_widget(lbl)
			self.ids['k_x'+ str(i+1)] = txtI

		return self.lay_out
	

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


