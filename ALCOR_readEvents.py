import os
import glob
import sys

import binascii

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.optimize import curve_fit
#from scipy import asarray as ar,exp
from scipy.stats import norm
import pandas as pd
import pickle

def gaus(x, a, mu, sigma):
	return a * np.exp( -np.power( (x - mu)/sigma, 2.0 ) / 2.0)

def fermi_dirac(x, a, mu, sigma):
	return a / ( np.exp( (x-mu) / sigma) + 1)

def fermi_dirac_2(x, a, mu, sigma):
	return a * ( -1 / ( np.exp( (x-mu) / sigma) + 1) + 1 )


Win_path = "C:/Users/Fabio/Documents/python_conda/"
Linux_path = "/home/fabio/work/ALCOR/ALCOR_data/"


OS = sys.platform
if OS == 'win32':
	op_sys = "WINDOWS"
	path = Win_path
	data_path = path + "data/ALCOR_data/scan/"
	outDir = path + "outputs/ALCOR/"
	print("Windows operating system\n\n")
	#sep = '\\'
	sep = '/'
elif OS == 'linux2' or OS == 'linux':
	op_sys = "LINUX"
	path = Linux_path
	data_path = path + "data/ALCOR_data/scan/"
	outDir = path + "outputs/ALCOR/"
	print("Linux operating system\n\n")
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	print("Exit Program\n\n")
	sys.exit()


data_path = outDir + "decoded_data/"


#date = "04082021/"
date = "25082021/"

try:
	#print(sys.argv)
	RUN = sys.argv[1]
	filename = data_path + date + "RUN_{}_pickle.gz".format(RUN)
except:
	sys.exit(0)




########################################################################
########################################################################

print("Loading file {}...".format(filename))
df = pd.read_pickle(filename, compression="gzip")
print("File loaded.\n")

########################################################################
########################################################################


num_entries = df.shape[0]
print("Number of entries = {}".format(num_entries))

datarate_0 = num_entries / 5.0 / 1000.0
print("Rate = {} kHz".format(datarate_0))

for tdc_id in range(0,4):
	print("TDC {}: {} entries".format( tdc_id, len(df[df.tdc==tdc_id]) ) )


print("\nApply cut on Tfine = 0")
sel_df = df[df.Tfine!=0]
N = len(sel_df.index)
datarate_1 = N / 5.0 / 1000.0
print("Rate = {} kHz".format(datarate_1))

for tdc_id in range(0,4):
	print("TDC {}: {} entries".format( tdc_id, len(sel_df[sel_df.tdc==tdc_id]) ) )


is_check_tdc = True

if is_check_tdc:

	df0 = df[df.tdc==0]
	df1 = df[df.tdc==1]
	df2 = df[df.tdc==2]
	df3 = df[df.tdc==3]

	#binning = np.arange(0, 500, 1)
	#plt.hist(df0.Tfine, bins=binning)
	#plt.grid()
	#plt.show()


	y0 = df0.index
	y1 = df1.index
	y2 = df2.index
	y3 = df3.index

	x0 = range(0, len(y0))
	x1 = range(0, len(y1))
	x2 = range(0, len(y2))
	x3 = range(0, len(y3))

	plt.figure(1, figsize=(12,6))
	plt.plot(x0, y0, color='red', label="TDC0", lw=2)
	plt.plot(x1, y1, color='black', label="TDC1", lw=2)
	plt.plot(x2, y2, color='blue', label="TDC2", lw=2)
	plt.plot(x3, y3, color='yellow', label="TDC3", lw=2)
	plt.legend(loc=2, fontsize=12)
	plt.grid()
	plt.tight_layout()
	plt.show()




is_tdc_calib = True

if is_tdc_calib:

	pix_num = 0
	TDC_LUT = dict()

	fig, axs = plt.subplots(2,2, figsize=(10,7), sharex=False)
	binning = np.arange(20, 151, 1)
	plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.2, hspace=0.2)
	color_list = ['red', 'blue', 'green', 'yellow']

	for tdc_id in range(4):
		data = df[(df.tdc==tdc_id) & (df.pixel==pix_num)].Tfine
		data.plot.hist(bins=binning, color=color_list[tdc_id], alpha=0.8, ax=axs[int(tdc_id/2)][tdc_id%2], label="TDC {}".format(tdc_id))
		#data0 = df[(df.tdc==0) & (df.pixel==pix_num)].hist(column="Tfine", bins=binning, color='red', alpha=0.8, ax=axs[0][0])
		axs[int(tdc_id/2)][tdc_id%2].set_xlabel('Tfine [digits]')
		axs[int(tdc_id/2)][tdc_id%2].grid()

		temp = data.value_counts(sort=False).sort_index()
		xdata = temp.index
		ydata = temp.values
		for i in range(min(xdata)):
			#print(i)
			xdata = np.append(xdata, i)
			ydata = np.append(ydata, 0)
		for i in range(max(xdata)+1, max(xdata)+20):
			#print(i)
			xdata = np.append(xdata, i)
			ydata = np.append(ydata, 0)
		y_fit = ydata[xdata>80]
		x_fit = xdata[xdata>80]
		popt, pcov = curve_fit(fermi_dirac, x_fit, y_fit, p0=[6000.0, 100.0, 0.5])
		#print(popt)
		MAX = popt[1]
		x = np.arange(0.0, 150.0, 0.1)
		y = fermi_dirac(x, *popt)
		axs[int(tdc_id/2)][tdc_id%2].plot(x, y, "--", color="black", lw=2, label="MAX = {0:.1f}".format(MAX))

		y_fit = ydata[xdata<60]
		x_fit = xdata[xdata<60]
		popt, pcov = curve_fit(fermi_dirac_2, x_fit, y_fit, p0=[6000.0, 40.0, 0.5])
		#print(popt)
		MIN = popt[1]
		x = np.arange(0.0, 150.0, 0.1)
		y = fermi_dirac_2(x, *popt)
		axs[int(tdc_id/2)][tdc_id%2].plot(x, y, "--", color="black", lw=2, label="MIN = {0:.1f}".format(MIN))
		
		TDC_LUT[tdc_id] = [MAX, MIN]
	
		plt.setp(axs[int(tdc_id/2)][tdc_id%2], title="TFine (Pixel {}, TDC {})".format(pix_num, tdc_id))
		axs[int(tdc_id/2)][tdc_id%2].legend(loc=3, fontsize=10)



	fig.tight_layout()
	plt.show()
	#plt.plot(x, y, "--o", color="blue")
	#plt.show()



	clk_period = 3.125
	#MIN = [74.3, 69.1, 81.7, 75.8]
	#MAX = [205.9, 196.1, 211.1, 201.0]

	TDC_bin = [clk_period / (TDC_LUT[tdc][0] - TDC_LUT[tdc][1]) for tdc in TDC_LUT.keys()]
	TDC_CUT = [(TDC_LUT[tdc][0] + TDC_LUT[tdc][1]) / 2.0 for tdc in TDC_LUT.keys()]

	print(TDC_LUT)
	print(TDC_bin)
	print(TDC_CUT)

###############################################################################
###############################################################################








##################################################################
##################################################################


is_hit_map = False

if is_hit_map:

	pixel_hits = list()

	plt.figure(10, figsize=(12,8))
	binning = range(0, 33)
	plt.hist(pixel_hits, bins=binning)
	plt.yscale("log")
	plt.ylim([1, None])
	plt.xticks( np.arange(0, 33, 2) )
	plt.title("Pixel hit-map")
	plt.xlabel("pixel")
	plt.ylabel("N")
	plt.grid()
	plt.show()

##################################################################
##################################################################

