from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window

import os

#mesh functions
import sys
#adding path to source directory
sys.path.insert(0, 'd:/Proyectos_GitHub/dev_mode/src')

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
		self.ids.limit_layer.text=os.path.join(path, filename[0])
		print(self.ids)		
		self.dismiss_popup()

	def mesh(self):
		print('eres puto')
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