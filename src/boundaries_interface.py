import kivy
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App

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
	pass


#class MainApp(App):
#	def build(self):		
#		return gwf_interface()



#MainApp().run()