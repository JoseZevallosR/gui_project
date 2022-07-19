import kivy
from kivy.lang import Builder
from kivy.app import App
#from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView

from kivy.properties import ObjectProperty,StringProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
from kivy.clock import Clock

#check
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
from boundaries_interface import *
from popups_dialog import *
#check
from vertical_layers import *

#modflow
import flopy
import flopy.discretization as fgrid
import flopy.plot as fplot
from flopy.utils.gridintersect import GridIntersect
import flopy.utils.binaryfile as bf
import matplotlib.pyplot as plt
from flopy.utils import HeadFile
from flopy.export import vtk

import numpy as np
from scipy.interpolate import griddata
from osgeo import osr
from osgeo import gdal
from osgeo import gdal_array
import rasterio
from rasterio.transform import from_origin
import geopandas as gpd
import json
import pyvista as pv

from shapely.geometry import mapping
from shapely.geometry import Polygon, Point, MultiLineString
from collections import OrderedDict
import pandas as pd

#rasters
import rasterio
from rasterio.transform import from_origin
import contextily as cx #background maps

Builder.load_file('../kv/tabs.kv')


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

		#Boundaries conditions layouts
		self.gwf_widget=gwf_interface()
		self.gwfnpf_widget=gwfnpf_interface()
		self.gwfrcha_widget=gwfrcha_interface()
		self.gwfevta_widget= gwfevta_interface()
		self.gwfevt_widget= gwfevt_interface()
		self.gwfdrn_widget=gwfdrn_interface()
		self.gwfsto_widget=gwfsto_interface()
		self.gwfghb_widget=gwfghb_interface()
		self.gwfchd_widget=gwfchd_interface()

		self.gwfic_widget=gwfic_interface()
		self.tdis_widget=tdis_interface()

		self.gwfrch_widget=gwfrch_interface()
		self.gwfriv_widget=gwfriv_interface()
		self.gwfuzf_widget=gwfuzf_interface()
		self.gwfwel_widget=gwfwell_interface()
		self.gwfoc_widget=gwfoc_interface()


		#Keeps track of bc set by the user for the gwf model
		self.checkbox_BC_dict={}
		self.checkbox_BC_dict['tdis']=False
		self.checkbox_BC_dict['gwf']=False
		self.checkbox_BC_dict['gwf_drn']=False
		self.checkbox_BC_dict['gwf_evt']=False
		self.checkbox_BC_dict['gwf_evta']=False
		self.checkbox_BC_dict['gwf_ghb']=False
		self.checkbox_BC_dict['gwf_chd']=False
		self.checkbox_BC_dict['gwf_gnc']=False
		self.checkbox_BC_dict['gwf_gwt']=False
		self.checkbox_BC_dict['gwf_hfb']=False
		self.checkbox_BC_dict['gwf_ic']=False
		self.checkbox_BC_dict['gwf_lak']=False
		self.checkbox_BC_dict['gwf_maw']=False
		self.checkbox_BC_dict['gwf_mvr']=False
		self.checkbox_BC_dict['gwf_nam']=False
		self.checkbox_BC_dict['gwf_npf']=False
		self.checkbox_BC_dict['gwf_oc']=False
		self.checkbox_BC_dict['gwf_rch']=False
		self.checkbox_BC_dict['gwf_rcha']=False
		self.checkbox_BC_dict['gwf_riv']=False
		self.checkbox_BC_dict['gwf_sfr']=False
		self.checkbox_BC_dict['gwf_sto']=False
		self.checkbox_BC_dict['gwf_uzf']=False
		self.checkbox_BC_dict['gwf_wel']=False


		#review this part for vertical mesh
		self.offsets_layer=offsets_layers()
		self.dems_layer=dems_layers()
			

	# POPUP HANDLERS 
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
		self._popup = Popup(title="Save Project", content=content,
                            size_hint=(0.9, 0.9))
		self._popup.open()

	def create_project(self,path,filename):

		self.directory_path = os.path.join(path, filename)
		self.ids['project_path'].text = os.path.join(path, filename)
		

		if not os.path.isdir(self.directory_path):
		    os.makedirs(self.directory_path, exist_ok=True)

		sub_directories = ['/shps','/rst','/model','/json','/vtk']

		directories = [Path(self.directory_path+folder) for folder in sub_directories]
		for workspace in directories:
		    workspace.mkdir(exist_ok=True)
	    
		self.dismiss_popup()

	def voronoi_mesh_loading(self):
		#review here
		content = ProgresBarrDialog(self)
		self.popup = Popup(title = 'Meshing',content=content ,size_hint=(0.5,0.5))
		self.popup.open()

		threading.Thread(target=partial(self.mesh,content)).start()

	def mesh(self,content):

		if self.ids['project_path'].text!='':
			self.directory_path=self.ids['project_path'].text

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
		#vorMesh.getPointsAsShp('vertexOrg',outPath+'/vertexOrg.shp')
		#vorMesh.getPointsAsShp('vertexDist',outPath+'/vertexDist.shp')
		#vorMesh.getPointsAsShp('vertexBuffer',outPath+'/vertexBuffer.shp')
		#vorMesh.getPointsAsShp('vertexMaxRef',outPath+'/vertexMaxRef.shp')
		#vorMesh.getPointsAsShp('vertexMinRef',outPath+'/vertexMinRef.shp')
		#vorMesh.getPointsAsShp('vertexTotal',outPath+'/vertexTotal.shp')
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
		mesh=gpd.read_file(self.directory_path+'/shps/voronoiRegions.shp')
		ax = mesh.plot(figsize=(10, 10), alpha=0.2, edgecolor='k')
		cx.add_basemap(ax,crs=mesh.crs.to_string())
		#tgr = fgrid.VertexGrid(self.vertices, self.cell2d)
		#fig, ax = plt.subplots(1, 1, figsize=(15, 10))
		#pmv = fplot.PlotMapView(modelgrid=tgr)
		#pmv.plot_grid(ax=ax)
		box = self.ids.boxs
		box.clear_widgets()
		box.add_widget(FigureCanvasKivyAgg(plt.gcf()))

	def checkbox_layers_dem(self,instance,value):
		if value== True:
			self.ids.layers_box.clear_widgets()
			self.ids.layers_box.add_widget(self.dems_layer.add_layers(self.ids.number_layers.text))
		else:
			self.ids.layers_box.clear_widgets()
		pass


	def checkbox_offsets(self,instance,value):
		# adding text inputs according to the number of desire layers
		nlay = int(self.ids.number_layers.text)
		self.npf_properties=self.gwfnpf_widget.add_layers(nlay)# this line creates the number of ks necessary
		if value == True:
			self.ids.layers_box.clear_widgets()			
			self.ids.layers_box.add_widget(self.offsets_layer.add_layers(self.ids.number_layers.text))
		else:
			self.ids.layers_box.clear_widgets()
		pass

	def vertical_mesh_loading(self):
		#review here
		content = ProgresBarrDialog(self)
		self.popup = Popup(title = 'Vertical Meshing',content=content ,size_hint=(0.5,0.5))
		self.popup.open()

		threading.Thread(target=partial(self.vertical_mesh,content)).start()


	def vertical_mesh(self,content):
		if self.ids['project_path'].text!='':
			self.directory_path=self.ids['project_path'].text

		def next(*args):
			
			if content.ids['my_progress_bar'].value <= 99:
				content.ids['my_progress_bar'].value +=1
				
		content = content

		"review this"
		nlay = int(self.ids.number_layers.text)#number of layers
		src = rasterio.open(self.ids.dem_layer.text)
		elevation=[x for x in src.sample(self.centroids)]
		mtop=np.array([elev[0] for i,elev in enumerate(elevation)])
		zbot=np.zeros((nlay,self.ncpl))

		AcuifInf_Bottom = float(self.ids.bottom_layer.text)

		zbot[nlay-1,] = AcuifInf_Bottom

		top_bottom_dif= mtop-AcuifInf_Bottom

		if len(self.offsets_layer.ids)!=0:
			for i,x in enumerate(self.offsets_layer.ids):
				zbot[i,]=AcuifInf_Bottom+float(self.offsets_layer.ids[x].text)*top_bottom_dif
				
			print(zbot)#erase this later
			self.mtop=mtop
			self.zbot=zbot #check here
		if len(self.dems_layer.ids)!=0:
			for x in self.dems_layer.ids:
				print(x)

		Clock.schedule_interval(next,1/100)

	def checkbox_gwf(self,instance,value):
		#clicked = True, unclicked is false
		
		if value == True:
			self.checkbox_BC_dict['gwf']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwf_widget)
		else:
			self.checkbox_BC_dict['gwf']=False
			self.ids.boundary_box.clear_widgets()
		pass
	def checkbox_npf(self,instance,value):
		#clicked = True, unclicked = false

		if value == True:
			self.checkbox_BC_dict['gwf_npf']=True
			#displaying the number of properties necessary for the model
			self.ids.boundary_box.clear_widgets()
			self.gwfnpf_widget.ids.npf_box.add_widget(self.npf_properties)
			self.ids.boundary_box.add_widget(self.gwfnpf_widget)
		else:
			self.checkbox_BC_dict['gwf_npf']=False
			self.ids.boundary_box.clear_widgets()
			self.gwfnpf_widget.ids.npf_box.clear_widgets()
		pass
	def checkbox_rcha(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_rcha']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfrcha_widget)
		else:
			self.checkbox_BC_dict['gwf_rcha']=False
			self.ids.boundary_box.clear_widgets()
		pass
	def checkbox_evta(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_evta']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfevta_widget)
		else:
			self.checkbox_BC_dict['gwf_evta']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_evt(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_evt']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfevt_widget)
		else:
			self.checkbox_BC_dict['gwf_evt']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_sto(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_sto']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfsto_widget)
		else:
			self.checkbox_BC_dict['gwf_sto']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_ghb(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_ghb']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfghb_widget)
		else:
			self.checkbox_BC_dict['gwf_ghb']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_chd(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_chd']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfchd_widget)
		else:
			self.checkbox_BC_dict['gwf_chd']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_rch(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_rch']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfrch_widget)
		else:
			self.checkbox_BC_dict['gwf_rch']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_riv(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_riv']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfriv_widget)
		else:
			self.checkbox_BC_dict['gwf_riv']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_uzf(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_uzf']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfuzf_widget)
		else:
			self.checkbox_BC_dict['gwf_uzf']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_wel(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_wel']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfwel_widget)
		else:
			self.checkbox_BC_dict['gwf_wel']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_oc(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_oc']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfoc_widget)
		else:
			self.checkbox_BC_dict['gwf_oc']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_tdis(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['tdis']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.tdis_widget)
		else:
			self.checkbox_BC_dict['tdis']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_ic(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_ic']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfic_widget)
		else:
			self.checkbox_BC_dict['gwf_ic']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def checkbox_drn(self,instance,value):
		#clicked = True, unclicked = false
		
		if value == True:
			self.checkbox_BC_dict['gwf_drn']=True
			self.ids.boundary_box.clear_widgets()
			self.ids.boundary_box.add_widget(self.gwfdrn_widget)
		else:
			self.checkbox_BC_dict['gwf_drn']=False
			self.ids.boundary_box.clear_widgets()
		pass

	def spinner_clicked(self,value):
		#check this later for displaying dropdown option values
		print(value)


	def running_model_loading(self):
		#review here
		content = ProgresBarrDialog(self)
		self.popup = Popup(title = 'Model creating and running ...',content=content ,size_hint=(0.5,0.5))
		self.popup.open()

		threading.Thread(target=partial(self.create_model_gwf,content)).start()

	def create_model_gwf(self,content):
		#Bar loading
		if self.ids['project_path'].text!='':
			self.directory_path=self.ids['project_path'].text

		def next(*args):
			
			if content.ids['my_progress_bar'].value <= 99:
				content.ids['my_progress_bar'].value +=1
				
		content = content

		# create simulation
		model_name = self.ids.model_name.text
		model_ws = self.directory_path+'/model'
		exe_name = '../exe/mf6.exe'

		sim = flopy.mf6.MFSimulation(sim_name=model_name, version='mf6', exe_name=exe_name,sim_ws=model_ws)

		
		# create iterative model solution and register the gwf model with it
		ims = flopy.mf6.ModflowIms(sim, linear_acceleration='BICGSTAB')
		# create gwf model
		gwf = flopy.mf6.ModflowGwf(sim, modelname=model_name, save_flows=True, newtonoptions=['under_relaxation'])

		# disv
		nlay = int(self.ids.number_layers.text)
		disv = flopy.mf6.ModflowGwfdisv(gwf, nlay=nlay, ncpl=self.ncpl,top=self.mtop, botm=self.zbot,nvert=self.nvert, vertices=self.vertices,cell2d=self.cell2d)

		if self.checkbox_BC_dict['gwf_npf']==True:
			Kx = [float(self.gwfnpf_widget.ids['k_x'+ str(i+1)].text) for i in range(nlay)] #take the values from widget
			icelltype = [int(self.gwfnpf_widget.ids['type_i'+ str(i+1)].text) for i in range(nlay)]
			npf = flopy.mf6.ModflowGwfnpf(gwf,save_specific_discharge=True,icelltype=icelltype,k=Kx)

		if self.checkbox_BC_dict['tdis']==True:
			pass

		# create tdis package
		tdis_rc = [(1.0, 1, 1.0)]
		nper=len(tdis_rc)
		tdis = flopy.mf6.ModflowTdis(sim, nper=nper, time_units='seconds',perioddata=tdis_rc)

		if self.checkbox_BC_dict['gwf_ic']==True:
			pass
		ic = flopy.mf6.ModflowGwfic(gwf, strt=np.stack([self.mtop for i in range(nlay)]))

		if self.checkbox_BC_dict['gwf_sto']==True:
			pass

		if self.checkbox_BC_dict['gwf_oc']==True:
			pass

		if self.checkbox_BC_dict['gwf_chd']==True:
			pass

		if self.checkbox_BC_dict['gwf_ghb']==True:
			pass

		if self.checkbox_BC_dict['gwf_rcha']==True:
			rchr = float(self.gwfrcha_widget.ids['rcha_rate'].text)
			rch = flopy.mf6.ModflowGwfrcha(gwf, recharge=rchr)

		if self.checkbox_BC_dict['gwf_rch']==True:
			pass

		if self.checkbox_BC_dict['gwf_wel']==True:
			pass

		##### Head - Dependent #####
		if self.checkbox_BC_dict['gwf_drn']==True:

			tgr = fgrid.VertexGrid(self.vertices, self.cell2d)
			ix2 = GridIntersect(tgr)
			#data from gui
			rios=gpd.read_file(self.gwfdrn_widget.ids['drain_shape'].text) #river layer
			list_rivers=[]
			for i in range(rios.shape[0]):
			    
			    list_rivers.append(rios['geometry'].loc[i])
			    
			mls = MultiLineString(lines=list_rivers)
			#intersec rivers with our grid
			result=ix2.intersect(mls)
			#stress_period_data : [cellid, elev, cond, aux, boundname]
			drain_list = []
			for i in result.cellids:
			    drain_list.append([0,i,self.mtop[i],0.001])
			drain_spd = {0:drain_list}
			drn = flopy.mf6.ModflowGwfdrn(gwf,stress_period_data=drain_spd)

		if self.checkbox_BC_dict['gwf_evta']==True:
			evtr = float(self.gwfevta_widget.ids['evta_rate'].text)#1.2/365/86400
			evt = flopy.mf6.ModflowGwfevta(gwf,ievt=1,surface=self.mtop,rate=evtr,depth=1.0)

		if self.checkbox_BC_dict['gwf_evt']==True:
			pass

		if self.checkbox_BC_dict['gwf_riv']==True:
			pass

		##### Advance Package #####
		if self.checkbox_BC_dict['gwf_uzf']==True:
			pass

		print(self.checkbox_BC_dict)

		hname = '{}.hds'.format(model_name)
		cname = '{}.cbc'.format(model_name)
		oc = flopy.mf6.ModflowGwfoc(gwf, budget_filerecord=cname,
		 head_filerecord=hname,
		 saverecord=[('HEAD', 'ALL'), ('BUDGET',
		'ALL')])

		self.gwf =gwf

		sim.write_simulation()
		sim.run_simulation()

		Clock.schedule_interval(next,1/50)
		pass
		#content.ids['my_progress_bar']
	
	def plot_heads(self):
		model_name = self.ids.model_name.text
		model_ws = self.directory_path+'/model'

		hds = bf.HeadFile(model_ws+'/'+model_name + '.hds')
		head = hds.get_data(totim=1.0)
		head[head==1e+30]=np.nan
		cpth = os.path.join(model_ws, model_name+'.cbc')
		cobj = flopy.utils.CellBudgetFile(cpth, precision=hds.precision)
		spd = cobj.get_data(text='DATA-SPDIS')[0]


		plt.gcf()
		fig = plt.figure(figsize=(10, 15))
		ax = fig.add_subplot(1, 1, 1, aspect='equal')
		mapview = flopy.plot.PlotMapView(model=self.gwf)

		quadmesh = mapview.plot_array(head, alpha=0.5)
		levels = np.linspace(np.nanmin(head),np.nanmax(head),num=50)
		c = mapview.contour_array(head, linewidths=0.75,colors='white',levels=levels)
		plt.clabel(c, fmt='%3d')
		plt.colorbar(quadmesh, shrink=0.75)

		box = self.ids.results2d
		box.clear_widgets()
		box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
		pass

	def plot_xs(self):
		pass

	def plot_specificQ(self):
		model_name = self.ids.model_name.text
		model_ws = self.directory_path+'/model'

		hds = bf.HeadFile(model_ws+'/'+model_name + '.hds')
		head = hds.get_data(totim=1.0)
		head[head==1e+30]=np.nan
		cpth = os.path.join(model_ws, model_name+'.cbc')
		cobj = flopy.utils.CellBudgetFile(cpth, precision=hds.precision)
		spd = cobj.get_data(text='DATA-SPDIS')[0]

		head = self.gwf.output.head().get_data()
		bdobj = self.gwf.output.budget()

		plt.gcf()
		fig = plt.figure(figsize=(15, 15))
		ax = plt.subplot(1, 1, 1)
		pmv = flopy.plot.PlotMapView(self.gwf)
		pmv.plot_array(head, cmap="jet", alpha=0.5)
		pmv.plot_vector(spd["qx"], spd["qy"], alpha=0.25);

		box = self.ids.results2d
		box.clear_widgets()
		box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
		pass

	def save_current_2d(self):
		#box = self.ids.results2d
		#box.export_to_png()
		pass

	def plot3D(self):
		#grid=pv.read('C:/Users/saulm/Documents/jose_Z/vtk_files/model_output_test/regional_model_000000.vtk')
		#grid = grid.cast_to_unstructured_grid()
		#grid.plot(color='w', show_edges=True, show_bounds=True)
		#plt.show()
		print(self.gwfnpf_widget.ids)
		#Boundaries conditions layouts
		print(self.gwf_widget.ids)
		print(self.gwfnpf_widget.ids)
		print(self.gwfrcha_widget.ids)
		print(self.gwfevta_widget.ids)
		print(self.gwfdrn_widget.ids)

		#export heads to vtk format
		model_name = self.ids.model_name.text
		model_ws = self.directory_path+'/model'


		head_vtk_path=self.directory_path+'/vtk'

		head_file = os.path.join(model_ws, model_name+".hds")
		hds = HeadFile(head_file)


		# create the vtk object and export heads
		vtkobj = vtk.Vtk(self.gwf, xml=True, pvd=False, vertical_exageration=1)
		vtkobj.add_heads(hds)
		vtkobj.write(os.path.join(head_vtk_path,"Heads_VTK","regional_model_head.vtu"))



	
		


class MainApp(App):
	def build(self):		
		return TupacMaster()


MainApp().run()