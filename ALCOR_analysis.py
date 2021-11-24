import os
import sys
import glob


import numpy as np
import matplotlib.pylab as plt
from scipy.optimize import curve_fit
import math


import ALCOR_data as d1



def func_lin(x, a, b):
	return a * x + b





class Analysis:

	def __init__(self):
		print("\nInitializing class for analysis\n")

	def import_data(self, mainDir, filename, is_avoid_nan = False):

		self._mainDir = mainDir
		
		self._file_name, self._ext = os.path.splitext(filename)
		
		#filenames = sorted(glob.glob(self._mainDir + filename))
		#self._file_name, self._ext = os.path.splitext( os.path.split(filenames[0])[1] )

		self.FIFO_len = 2048 					#int(self.my_data.get_config('TP num pulses')[1])

		self.my_data = d1.Import_Data(mainDir, filename, is_avoid_nan)

		self.channels = self.my_data.channels
		self.bParam = self.my_data.bParam
		self.aParam = self.my_data.get_data(self.channels[0], self.bParam[0], 'paramA')
		self.attributes = self.my_data.attributes
		
		self.is_num_pulses = False
		is_clk_freq = False

		for config in self.my_data.get_config(" "):

			if config[0] == 'Clock frequency (MHz)':
				is_clk_freq = True		
				self.clk_freq = float(self.my_data.get_config('Clock frequency (MHz)')[1])		## MHz
			elif config[0] == 'TP disable' and config[1] == '0':
				self.is_num_pulses = True
			elif config[0] == 'Use 81133A' and config[1] == '1':
				self.is_num_pulses = True
			elif config[0] == 'TP num pulses': #and self.is_num_pulses == True:
				self.num_pulses = int(self.my_data.get_config('TP num pulses')[1])
			elif config[0] == 'Threshold file':
				self.vth_file = config[1].split('\\')[-1]
				print("\n\nVTH file")
				print(self.vth_file)

		if not(is_clk_freq):
			self.clk_freq = 320.0

		self.clk_period = 1000. / self.clk_freq				## ns




class TDC(Analysis):

	def __init__(self, mainDir, filename, outDir):

		self._main_Dir = mainDir
		self._file_name = filename
		self._outdir = outDir

		self.import_data(self._main_Dir, self._file_name)

		#print(self._main_Dir)
		#print(self._file_name)



	def do_something_with_config(self, param = "dummy", opt1 = 0, opt2 = False):
		
		cfg_val = self.my_data.get_config(param)[1]

		print("{} = {}\n\n".format(param, cfg_val))


	def do_something_with_data(self, opt1 = 0, opt2 = False, opt3 = "calib"):

		x_T = self.my_data.get_data(0, 0, 'paramA')
		y_T = self.my_data.get_data(0, 0, 'TFine_M')

		print("Phase = {}\n".format(x_T))
		print("TFine = {}\n".format(y_T))


######################################################################################################################
######################################################################################################################


class VTH(Analysis):

	def __init__(self, mainDir, filename):

		self._main_Dir = mainDir
		self._file_name = filename

		self.import_data(self._main_Dir, self._file_name)


	def do_vth_scan(self, pix = 0, saveImg = False, doFit = False):

		print("Analyzing pixel n.{} ...".format(pix))

		x = self.my_data.get_data(pix, 0, 'paramA')
		y = self.my_data.get_data(pix, 0, 'tot_events')		## sel_events
		#print(x)
		#print(y)

		plt.plot(x, y, 'b--o')
		plt.grid()
		plt.show()
