#########################################################################################
#########################################################################################

import os
import sys
import math




#########################################################################################
#########################################################################################



class Import_Data:
	"""
	class to import data from LabVIEW txt file
	"""
	def __init__(self, mainDir, filename, is_avoid_nan = False):

		self.labVIEW_data, self.labVIEW_config = self.imp_data(os.path.join(mainDir, filename))

		#print(self.labVIEW_data[0].keys())

		self.channels = list( self.labVIEW_data.keys() )
		self.bParam = list( self.labVIEW_data[self.channels[0]].keys() )
		self.attributes = list( self.labVIEW_data[self.channels[0]][self.bParam[0]].keys() )

		if is_avoid_nan:
			for ch in self.channels:
				for b in self.bParam:
					self.avoid_nan(ch, b)


#########################################################################################


	def avoid_nan(self, channel, parB):
		count = 0
		del_list = []
		copy_list = list(self.labVIEW_data[channel][parB]['TCoarse_M'])
		for i, test_data in enumerate(copy_list):
			#print(test_data)
			if math.isnan(test_data):
				#print("Removing point: {} (NaN)".format(self.labVIEW_data[channel][parB]['paramA'][i-count]))
				for attribute in self.attributes:
					if attribute == 'paramA':
						del_list.append(self.labVIEW_data[channel][parB][attribute].pop(i-count)) 
					else:
						del self.labVIEW_data[channel][parB][attribute][i-count]
				count += 1
		if count > 1:
			pass
			#print("\nAvoid NaN for ch = {}, B = {}".format(channel, parB))
			#print("Removed {} points".format(count))
			#print("Deleted points: {}\n".format(sorted(del_list)))


#########################################################################################


	def get_data(self, channel, parB, attribute):

		return self.labVIEW_data[channel][parB][attribute]


#########################################################################################


	def get_config(self, attribute = "dummy"):
		for field in self.labVIEW_config:
			if field[0] == attribute:
				return field
				break
		return self.labVIEW_config


#########################################################################################


	def get_Astep_number(self):

		return self._num_parA


#########################################################################################


	def get_Bstep_number(self):

		return self._num_parB


#########################################################################################


	def get_ch_number(self):

		return self._numCH


#########################################################################################


	#def get_thr_path(self):

		#return self._vthPath


#########################################################################################

	def imp_data(self, filename):

	### FUNCTION TO IMPORT DATA FROM LABVIEW TXT FILE

		if os.path.isfile(filename) and os.access(filename, os.R_OK):
		    print("File exists and is readable")
		else:
		    print("Either file is missing or is not readable")
		    sys.exit()


		try:
			
			with open(filename, 'r') as f:

				data = dict()

				## Header
				f.readline()

				## Run info
				self._numCH, self._num_parB, self._num_parA, self._num10b8bErr = [int(x) for x in f.readline().split(" ")]
				print(self._numCH, self._num_parB, self._num_parA)

				## Keys
				temp = f.readline().split("\r")[0].split(" ")
				keys = [x.split("_", 1)[1] for x in temp]
				#print("\nKEYS = {}\n".format(keys))
				
				## First channel number
				ch = int(temp[0].split("_")[0][2:])
				
				## Channels data
				for channel in range(0, self._numCH):
					ch_data = dict()
					
					if channel > 0:
						ch = int(f.readline().split("_", 1)[0][2:])
					#print("\nCHANNEL n.{}".format(ch))

					for b in range(0, self._num_parB):
						B_data = []
						data_B = dict()
						for a in range(0, self._num_parA):
							B_data.append(f.readline().split(" "))

						for i, key in enumerate(keys):
							data_B[key] = [float(x[i]) for x in B_data]			# dictionary for data of single param B value

						ch_data[b] = data_B										# dictionary for data of single channel

					data[ch] = ch_data											# dictionary for data of all channels



				## Check End of Data
				temp = f.readline().split("<")[1].split(">")[0]
				#print(temp)
				if temp != "Cluster":
					print("ERROR while reading file: expected 'Cluster', got {}\n\n".format(temp))


				configurations = f.readlines()
				

			## File closed

			#########################################################################################

		except OSError:

			print('Well darn (OS Error).')



		parameters = []
		values = []


		for i, config in enumerate(configurations):
			
			temp = config.split(">")
			if temp[0][1:] == "Name":
				temp = temp[1].split("<")[0]
				if temp != "Numeric":
					if configurations[i+1].split(">")[0][1:] == "Val":
						parameters.append(temp)
						values.append(configurations[i+1].split(">")[1].split("<")[0])
					elif configurations[i+1].split(">")[0][1:] == "NumElts":
						parameters.append(temp)
						values.append("{} elements".format(configurations[i+1].split(">")[1].split("<")[0]))
					elif configurations[i+1].split(">")[0][1:] == "Choice":
						j = 0
						while configurations[i+1+j].split(">")[0][1:] == "Choice":
							j += 1
							
						if configurations[i+1+j].split(">")[0][1:] == "Val":
							index = int(configurations[i+1+j].split(">")[1].split("<")[0])
							parameters.append(temp)
							values.append(configurations[i+1+index].split(">")[1].split("<")[0])
							if temp == "A":
								self.x_axis_name = values[-1]
							if temp == "B": #and values[-1] != "None":
								self.b_scan = values[-1]
						else:
							print("Error!!!")


		config_map = map( list, zip( *[parameters, values] ) )

		print("\nSCAN of {}\n".format(self.x_axis_name))
		if self.b_scan != "None":
			print("and SCAN of {}\n\n".format(self.b_scan))

		#print(l)


		config_list = [ parameter for i, parameter in enumerate(config_map) ]
		#print(config_list)
		
		
		with open(os.path.splitext(filename)[0] + "_config.txt", 'w') as config_file:
			for i, parameter in enumerate(config_map):
				print(parameter[0], parameter[1])
				config_file.write("{} = {}\n".format(parameter[0], parameter[1]))


		#for b in range(0, num_parB):
			#print("\n\n\nB = {}\n data = {}\n\n\n".format(b, ch_data[b]))


		return data, config_list


#########################################################################################
#########################################################################################