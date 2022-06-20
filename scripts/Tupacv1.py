import kivy
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
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


from kivy.clock import Clock

#check
from kivy.uix.filechooser import FileChooserListView

import os
import time
import threading
from functools import partial

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

Builder.load_file('tabs.kv')

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

class TupacMaster(TabbedPanel):
	loadfile = ObjectProperty(None)
	savefile = ObjectProperty(None)
	text_input = ObjectProperty(None)


	#variables to move around the class
	def __init__(self,**kwargs):
		super(TupacMaster,self).__init__(**kwargs)
		
		self.id_layer_text='' # path to each layer
		self.directory_path='' #path to project directory
		self.cell2d=0
		self.vertices=0
		self.ncpl = 0
		self.nvert = 0
		self.centroids=0

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

	def doit_in_thread(self):
		#review here
		content = ProgresBarrDialog(self)
		self.popup = Popup(title = 'Meshing',content=content ,size_hint=(0.5,0.5))
		self.popup.open()

		threading.Thread(target=partial(self.mesh,content)).start()

	def mesh(self,content):

		def next(*args):
			
			if content.ids['my_progress_bar'].value <= 99:
				content.ids['my_progress_bar'].value +=1
				
		content = content
		
				
		from geoVoronoi import createVoronoi
		#Create mesh object
		vorMesh = createVoronoi()

		#Define base refinement and refinement levels
		vorMesh.defineParameters(maxRef = int(self.ids.max_ref.text), minRef=int(self.ids.min_ref.text), stages=5)
	
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
		

		mesh=mesh_shape(self.directory_path+'/shps/voronoiRegions.shp')
		gridprops=mesh.get_gridprops_disv()
		self.cell2d = gridprops['cell2d']
		self.vertices = gridprops['vertices']
		self.ncpl = gridprops['ncpl']
		self.nvert = gridprops['nvert']
		self.centroids=gridprops['centroids']
		
		
		Clock.schedule_interval(next,1/50)

	def plot_mesh(self):
		#checkin mesh
		plt.gcf()
		tgr = fgrid.VertexGrid(self.vertices, self.cell2d)
		fig, ax = plt.subplots(1, 1, figsize=(15, 10))
		pmv = fplot.PlotMapView(modelgrid=tgr)
		pmv.plot_grid(ax=ax)
		box = self.ids.boxs
		box.clear_widgets()
		box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

	def add_layers(self,*args):
		i= len(self.ids.inner_box.children)
		lay_out=BoxLayout()
		btn = Button(
			text = "Load",
            size_hint = (0.05,0.05),
            height = "64dp"
			)
		txtI = TextInput(size_hint=(0.5,0.05))
		lay_out.add_widget(btn)
		lay_out.add_widget(txtI)
		self.ids['layer '+ str(i)] = txtI
		self.ids.inner_box.add_widget(lay_out)
		


class MainApp(App):
	def build(self):		
		return TupacMaster()


MainApp().run()