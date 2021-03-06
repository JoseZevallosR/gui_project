import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.app import App
from functools import partial
#https://www.pisciottablog.com/2020/11/03/python-kivy-bind-button-to-a-class-method-with-arguments/
from popups_dialog import *


class dems_layers(FloatLayout):

	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.dem_layout=FloatLayout(size_hint=(1,0.5))


	def dismiss_popup(self):
		self._popup.dismiss()
	def show_load(self,id_layer,*args):
		self.id_layer_text=id_layer
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content,size_hint=(0.9, 0.9))
		self._popup.open()

	def load(self, path, filename):
		self.ids[self.id_layer_text].text=os.path.join(path, filename[0])
		self.dismiss_popup()


	def add_layers(self,value,*args):
		#lay_out=FloatLayout(size_hint=(1,0.5))
		print(self.ids)
		if len(self.ids)!=value:
			for i in range(int(value)-2):
				btn = Button(text=f'Load DEM {i+2}',size_hint=(0.2,0.01),pos_hint={'x':0.05,'y':0.98-i*0.01})
				btn.bind(on_press=partial(self.show_load,'layer_'+ str(i)))
				txtI = TextInput(size_hint=(0.5,0.01),pos_hint={'x':0.3,'y':0.98-i*0.01})
				self.dem_layout.add_widget(btn)
				self.dem_layout.add_widget(txtI)
				self.ids['layer_'+ str(i+2)] = txtI
			return self.dem_layout

		else:
			return self.dem_layout
	

class offsets_layers(FloatLayout):

	def add_layers(self,value,*args):
		#lay_out=BoxLayout(orientation='vertical',size_hint=(1,0.5))
		lay_out= FloatLayout(size_hint=(1,0.5))

		for i in range(int(value)-1):
			lbl= Label(text=f'Bottom layer {i+1} (%)',size_hint=(0.2,0.01),pos_hint={'x':0.05,'y':0.98-i*0.01})
			txtI = TextInput(size_hint=(0.2,0.01),pos_hint={'x':0.3,'y':0.98-i*0.01})
			lay_out.add_widget(txtI)
			lay_out.add_widget(lbl)
			self.ids['layer_'+ str(i+1)] = txtI

		return lay_out
	pass