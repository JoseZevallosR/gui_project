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

	


tupackv = Builder.load_file('tupacbar.kv')

class TupacMaster(BoxLayout):

	loadfile = ObjectProperty(None)
	savefile = ObjectProperty(None)
	text_input = ObjectProperty(None)

	#Review this part to pass the id of the input text
	#id_input_text = StringProperty(None)
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.id_input_text=''


	def create_project(self):
		pass

	def dismiss_popup(self):
		self._popup.dismiss()
	def show_load(self,id_layer):
		self.id_input_text=id_layer
		content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
		self._popup = Popup(title="Load file", content=content,size_hint=(0.9, 0.9))
		self._popup.open()

	def load(self, path, filename):
		self.ids.limit_layer.text=os.path.join(path, filename[0])
		print(self.ids[self.id_input_text].text)	
		#print(id_inputext)	
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