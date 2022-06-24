
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
import os

class FileChooserI(FileChooserListView):
	path_tracker=os.path.abspath(os.sep)#u'/'#
	def on_submit(*args):
		print(args[1][0])

class ProgresBarrDialog(BoxLayout):
	def __init__(self, obj, **kwargs):
		super(ProgresBarrDialog, self).__init__(**kwargs)

# load and save dialog
class LoadDialog(FloatLayout):
	load = ObjectProperty(None)
	cancel = ObjectProperty(None)

class SaveDialog(Widget):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ProjectDialog(FloatLayout):
    
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    create_project = ObjectProperty(None)
