from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty,StringProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
import os

#mesh functions
import sys
#adding path to source directory
sys.path.insert(0, '../src')

# load and save dialog
class LoadDialog(Widget):
	load = ObjectProperty(None)
	cancel = ObjectProperty(None)

class SaveDialog(Widget):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ProjectDialog(Widget):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


tupackv = Builder.load_file('tupacbar.kv')

class TupacMaster(BoxLayout):

	loadfile = ObjectProperty(None)
	savefile = ObjectProperty(None)
	text_input = ObjectProperty(None)

	#Review this part to pass the id of the input text
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.id_input_text=''


	def create_project(self,path,filename):
		project_name = os.path.join(path, filename[0])

		if not os.path.isdir(project_name):
		    os.makedirs(project_name, exist_ok=True)

		sub_directories = ['/shps','/rst','/model','/json','/vtk']

		directories = [Path(project_name+folder) for folder in sub_directories]
		for workspace in directories:
		    workspace.mkdir(exist_ok=True)
		    
		self.dismiss_popup()

	def show_project(self):
		content = ProjectDialog(save=self.save, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def dismiss_popup(self):
		self._popup.dismiss()
	def show_load(self,id_layer):
		self.id_input_text=id_layer
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content,size_hint=(0.9, 0.9))
		self._popup.open()

	def load(self, path, filename):
		self.ids[self.id_input_text].text=os.path.join(path, filename[0])
		self.dismiss_popup()

	def show_save(self):
		content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def save(self, path, filename):
		with open(os.path.join(path, filename), 'w') as stream:
			stream.write(self.text_input.text)

		self.dismiss_popup()


	def mesh(self):
		
		from geoVoronoi import createVoronoi
		#Create mesh object
		vorMesh = createVoronoi()

		#Define base refinement and refinement levels
		vorMesh.defineParameters(maxRef = 500, minRef=50, stages=5)

		#Open limit layers and refinement definition layers
		#vorMesh.addLimit('basin','../examples/In/shp/Angascancha_Basin_Extension.shp')
		
		vorMesh.addLimit('basin',self.ids.limit_layer.text)
		vorMesh.addLayer('facilities','../examples/In/shp/rios.shp')

		#Generate point pair array
		vorMesh.extractOrgVertices()

		#Generate the point cloud and voronoi
		vorMesh.createPointCloud()
		vorMesh.generateVoronoi()

		#check or create an output folder
		outPath = '../examples/out/angascancha'

		if os.path.isdir(outPath):
		    print('The output folder %s exists'%outPath)
		else:
		    os.mkdir(outPath)
		    print('The output folder %s has been generated.'%outPath)

		#Export point data and voronoi polygons
		#Points
		vorMesh.getPointsAsShp('vertexOrg',outPath+'/vertexOrg.shp')
		vorMesh.getPointsAsShp('vertexDist',outPath+'/vertexDist.shp')
		vorMesh.getPointsAsShp('vertexBuffer',outPath+'/vertexBuffer.shp')
		vorMesh.getPointsAsShp('vertexMaxRef',outPath+'/vertexMaxRef.shp')
		vorMesh.getPointsAsShp('vertexMinRef',outPath+'/vertexMinRef.shp')
		vorMesh.getPointsAsShp('vertexTotal',outPath+'/vertexTotal.shp')
		#Polygons

		vorMesh.getPolyAsShp('voronoiRegions',outPath+'/voronoiRegions.shp')
		pass



class MainApp(MDApp):
	def build(self):
		self.theme_cls.theme_style = 'Dark'
		self.theme_cls.primary_palette = 'BlueGray'
		return TupacMaster()


MainApp().run()