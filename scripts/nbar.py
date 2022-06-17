from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty,StringProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout

import os
# self es para la clase que contiene el widget
#root se dirige a la identancio principal al parent
#app es la clase que corre todo el programa
#ObjecProperty nos sirve para declarar objetos en el archivo .py y despues asignarle valores en el .kv

#mesh functions
import sys
from pathlib import Path

Window.size = (1100,700)
#adding path to source directory
sys.path.insert(0, '../src')
from meshProperties import mesh_shape

import flopy.discretization as fgrid
import flopy.plot as fplot
import matplotlib.pyplot as plt

# load and save dialog
class LoadDialog(Widget):
	load = ObjectProperty(None)
	cancel = ObjectProperty(None)

class SaveDialog(Widget):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class ProjectDialog(Widget):
    
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    create_project = ObjectProperty(None)


tupackv = Builder.load_file('app.kv')

class TupacMaster(BoxLayout):

	loadfile = ObjectProperty(None)
	savefile = ObjectProperty(None)
	text_input = ObjectProperty(None)

	#variables to move around the class
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.id_layer_text=''
		self.directory_path=''


	def create_project(self,path,filename):
		self.directory_path = os.path.join(path, filename)


		if not os.path.isdir(self.directory_path):
		    os.makedirs(self.directory_path, exist_ok=True)

		sub_directories = ['/shps','/rst','/model','/json','/vtk']

		directories = [Path(self.directory_path+folder) for folder in sub_directories]
		for workspace in directories:
		    workspace.mkdir(exist_ok=True)
	    
		self.dismiss_popup()

	def show_project(self):
		content = ProjectDialog(create_project=self.create_project, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

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
		if self.ids.limit_layer.text != '':
			vorMesh.addLimit('Limit',self.ids.limit_layer.text)

		if self.ids.well_layer.text != '':
			vorMesh.addLayer('wells',self.ids.well_layer.text )
		if self.ids.river_layer.text != '':
			vorMesh.addLayer('rivers',self.ids.river_layer.text )
		if self.ids.drain_layer.text != '':
			vorMesh.addLayer('drains',self.ids.drain_layer.text )
		

		#Generate point pair array
		vorMesh.extractOrgVertices()

		#Generate the point cloud and voronoi
		vorMesh.createPointCloud()
		vorMesh.generateVoronoi()

		#check or create an output folder
		outPath = self.directory_path+'/shps'

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
		

	def plot_mesh(self):
		#checkin mesh
		mesh=mesh_shape('D:/Proyectos_GitHub/dev_mode/examples/out/angascancha/voronoiRegions.shp')
		gridprops=mesh.get_gridprops_disv()
		cell2d = gridprops['cell2d']
		vertices = gridprops['vertices']
		ncpl = gridprops['ncpl']
		nvert = gridprops['nvert']
		centroids=gridprops['centroids']

		tgr = fgrid.VertexGrid(vertices, cell2d)
		fig, ax = plt.subplots(1, 1, figsize=(15, 10))
		pmv = fplot.PlotMapView(modelgrid=tgr)
		pmv.plot_grid(ax=ax)
		box = self.ids.box
		box.add_widget(FigureCanvasKivyAgg(plt.gcf()))


class MainApp(MDApp):
	def build(self):
		self.theme_cls.theme_style = 'Dark'
		self.theme_cls.primary_palette = 'BlueGray'
		return TupacMaster()


MainApp().run()