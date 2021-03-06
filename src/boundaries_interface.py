import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.app import App

from popups_dialog import *

#Importing all the kvs
Builder.load_file('../kv/tdis.kv')

Builder.load_file('../kv/gwf.kv')
Builder.load_file('../kv/gwfic.kv')
Builder.load_file('../kv/gwfnpf.kv')
Builder.load_file('../kv/gwfrcha.kv')
Builder.load_file('../kv/gwfevta.kv')
Builder.load_file('../kv/gwfdrn.kv')

Builder.load_file('../kv/gwfevt.kv')
Builder.load_file('../kv/gwfghb.kv')
Builder.load_file('../kv/gwfchd.kv')
Builder.load_file('../kv/gwfgnc.kv')
Builder.load_file('../kv/gwfgwt.kv')
Builder.load_file('../kv/gwfhfb.kv')
Builder.load_file('../kv/gwflak.kv')
Builder.load_file('../kv/gwfmaw.kv')
Builder.load_file('../kv/gwfmvr.kv')
Builder.load_file('../kv/gwfnam.kv')
Builder.load_file('../kv/gwfoc.kv')
Builder.load_file('../kv/gwfrch.kv')
Builder.load_file('../kv/gwfriv.kv')
Builder.load_file('../kv/gwfsfr.kv')
Builder.load_file('../kv/gwfsto.kv')
Builder.load_file('../kv/gwfuzf.kv')
Builder.load_file('../kv/gwfwel.kv')


class tdis_interface(FloatLayout):
	pass

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
			lbl1= Label(text=f'K {i+1}',size_hint=(0.1,0.01),pos_hint={'x':0.05,'y':0.98-i*0.01})
			lbl2= Label(text=f'Type {i+1}',size_hint=(0.1,0.01),pos_hint={'x':0.4,'y':0.98-i*0.01})
			txtI1 = TextInput(size_hint=(0.1,0.01),pos_hint={'x':0.2,'y':0.98-i*0.01})
			txtI2 = TextInput(size_hint=(0.1,0.01),pos_hint={'x':0.5,'y':0.98-i*0.01})
			self.lay_out.add_widget(txtI1)
			self.lay_out.add_widget(txtI2)
			self.lay_out.add_widget(lbl1)
			self.lay_out.add_widget(lbl2)
			self.ids['k_x'+ str(i+1)] = txtI1
			self.ids['type_i'+str(i+1)] = txtI2

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


class gwfevt_interface(FloatLayout):
	pass

class gwfghb_interface(FloatLayout):
	pass

class gwfchd_interface(FloatLayout):
	pass

class gwfgnc_interface(FloatLayout):
	pass

class gwfgwt_interface(FloatLayout):
	pass

class gwfhfb_interface(FloatLayout):
	pass

class gwflak_interface(FloatLayout):
	pass

class gwfmaw_interface(FloatLayout):
	pass

class gwfmvr_interface(FloatLayout):
	pass

class gwfnam_interface(FloatLayout):
	pass

class gwfoc_interface(FloatLayout):
	pass

class gwfrch_interface(FloatLayout):
	pass

class gwfriv_interface(FloatLayout):
	pass

class gwfsfr_interface(FloatLayout):
	pass

class gwfsto_interface(FloatLayout):
	pass

class gwfuzf_interface(FloatLayout):
	pass

class gwfwell_interface(FloatLayout):
	pass