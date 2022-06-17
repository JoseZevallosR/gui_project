from kivy.lang import Builder
from kivy.app import App
#from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty,StringProperty

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

#check
from kivy.uix.filechooser import FileChooserListView

import os

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


class FileChooserI(FileChooserListView):
	path_tracker='C:/Users/saulm/Documents/jose_Z'
	def on_submit(*args):
		print(args[1][0])
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

class TupacMaster(TabbedPanel):
	loadfile = ObjectProperty(None)
	savefile = ObjectProperty(None)
	text_input = ObjectProperty(None)


	#variables to move around the class
	def __init__(self,**kwargs):
		super().__init__(**kwargs)
		self.id_layer_text='' # path to each layer
		self.directory_path='' #path to project directory

	# POP UP HANDLERS 
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

	def show_project(self):
		content = ProjectDialog(create_project=self.create_project, cancel=self.dismiss_popup)
		self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def create_project(self,path,filename):
		self.directory_path = os.path.join(path, filename)


		if not os.path.isdir(self.directory_path):
		    os.makedirs(self.directory_path, exist_ok=True)

		sub_directories = ['/shps','/rst','/model','/json','/vtk']

		directories = [Path(self.directory_path+folder) for folder in sub_directories]
		for workspace in directories:
		    workspace.mkdir(exist_ok=True)
	    
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
		mesh=mesh_shape(self.directory_path+'/shps/voronoiRegions.shp')
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
		box = self.ids.boxs
		box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

class MainApp(App):
	def build(self):		
		Builder.load_file('tabs.kv')
		return TupacMaster()


MainApp().run()