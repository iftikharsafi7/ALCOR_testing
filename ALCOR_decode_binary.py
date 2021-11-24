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


Win_path = "C:/Users/Fabio/Documents/python_conda/"
Linux_path = "/home/fabio/work/ALCOR/ALCOR_data/"


OS = sys.platform
if OS == 'win32':
	op_sys = "WINDOWS"
	path = Win_path
	data_path = path + "data/ALCOR_data/bin/"
	outDir = path + "outputs/ALCOR/decoded_data/"
	print("Windows operating system\n\n")
	sep = '/'
elif OS == 'linux2' or OS == 'linux':
	op_sys = "LINUX"
	path = Linux_path
	data_path = path + "data/ALCOR_data/bin/"
	outDir = path + "outputs/ALCOR/decoded_data/"
	print("Linux operating system\n\n")
	sep = '/'
else:
	print("ERROR: OS {} non compatible".format(OS))
	print("Exit Program\n\n")
	sys.exit()




#date = "20072021"
#date = "02082021"
#date = "03082021"
#date = "04082021"
#date = "05082021"
#date = "25082021"
#date = "30082021"

date = "04112021"

mainDir = data_path + date + sep
output_path = outDir + date + sep


try:
	#print(sys.argv)
	RUN = sys.argv[1]
	filename = mainDir + "RUN_{}.bin".format(RUN)
except:
	sys.exit(0)


is_txt = True

is_plot = True




######################################################
##				Decode binary data file				##
######################################################


print(output_path)

if is_txt:
	out_file = open("{}data_RUN_{}.txt".format(output_path, RUN), "w")
	k_file = open("{}decode.txt".format(output_path, RUN), "w")

n = 0
row_list = list()

cc = 0
is_CORRECTION = False
is_CRC = [False, False, False, False]
is_FRAME = [False, False, False, False]
is_STATUS = [False, False, False, False]
n_STATUS = [0, 0, 0, 0]

print(filename)

with open(filename, 'rb') as f:

	while (byte := f.read(1)):

		n += 1

		address = byte + f.read(1)
		n += 1
		fpga_add = address.hex()
		if fpga_add != "dcba":
			print("FPGA ADDRESS ERROR ({})!!!!!!!!!!!!!!!".format(fpga_add))
			sys.exit()


		pkt_num = f.read(4)
		n += 4
		packet_number = int.from_bytes(pkt_num, "big")


		pkt_len = f.read(2)
		n += 2
		packet_length =  int.from_bytes(pkt_len, "big")	

		
		if packet_number%1000 == 0:
			print("FPGA ADDRESS = {}".format(fpga_add))
			print("PACKET NUMBER = {}".format(packet_number) )
			print("PACKET LENGTH = {}\n".format(packet_length) )


		ev_data = f.read( packet_length - 8 ).hex()
		n += packet_length - 8
		
		#print(len(ev_data))
		#print(len(ev_data)/10)
		#print(int(len(ev_data)/10))
		#print(ev_data)
		#print(ev_data[-2:])


		##########################################################################################
		##########################################################################################


		if is_CORRECTION:
			for s in np.arange(0, 12, 2):
				first_event = ev_data[s : s+10]
				#print(first_event)
				if first_event[-4 : ] == '0000' or first_event[-4 : ] == '0100' or first_event[-4 : ] == '0200' or first_event[-4 : ] == '0300':
					temp_data = ev_data[s : ]
					#print("OK\n")
					#print(temp_data[6+10 : 10+10])
					if temp_data[6+10 : 10+10] == '0000' or temp_data[6+10 : 10+10] == '0100' or temp_data[6+10 : 10+10] == '0200' or temp_data[6+10 : 10+10] == '0300':
						#print("OK OK\n")
						ev_data = temp_data
						break


			#print(len(ev_data))
			#print(len(ev_data)/10)
			#print(int(len(ev_data)/10))
			#print(ev_data)
			#print(ev_data[-2:])

		##########################################################################################
		##########################################################################################


		for h in range(0, int(len(ev_data) / 10) ):
			temp = ev_data[ h * 10 : (h+1) * 10 ]
			print(temp)

			check = int(temp[9], 16) & 0x3				## 2 bits = AND of k-codes (0b00 --> event word, 0b11 --> check first 4 bytes of temp to confirm k-code) [last 2 bits]
			tx = (int(temp[9], 16) & 0xc ) >> 2			## 2 bits = TX (0,1,2,3) [previous 2 bits]
			zeros = (int(temp[8], 16) & 0xf)			## 4 bits = 0b0000 [previous 4 bits]
			#print(check, tx, zeros)
			if check == 3:													## K-codes word
				#print("This word may be a k-code word")
				#print("Check first 4 bytes of the word {}".format(temp))
				if (temp[0:2] == temp[2:4] == temp[4:6] == temp[6:8]):
					k_code = temp[0:2]
					#print("K-code = {} SECTOR = {}".format(k_code, tx))
					if k_code == "9c":
						print("CRC HEADER(sector {})".format(tx))
						k_file.write("CRC HEADER(sector {})\n".format(tx))
						out_file.write("CRC HEADER(sector {})\n".format(tx))
						is_CRC[tx] = True
					else:
						is_CRC[tx] = False
						if k_code == "1c":
							print("FRAME HEADER (sector {})".format(tx))
							k_file.write("FRAME HEADER (sector {})\n".format(tx))
							out_file.write("FRAME HEADER (sector {})\n".format(tx))
							is_FRAME[tx] = True
						else:
							is_FRAME[tx] = False
							if k_code == "5c":
								print("ROLLOVER HEADER(sector {})".format(tx))
								k_file.write("ROLLOVER HEADER(sector {})\n".format(tx))
								out_file.write("ROLLOVER HEADER(sector {})\n".format(tx))
							elif k_code == "bc":
								print("IDLE COMMA(sector {})".format(tx))
								k_file.write("IDLE COMMA(sector {})\n".format(tx))
								out_file.write("IDLE COMMA(sector {})\n".format(tx))
							elif k_code == "7c":
								print("STATUS HEADER(sector {})".format(tx))
								k_file.write("STATUS HEADER(sector {})\n".format(tx))
								out_file.write("STATUS HEADER(sector {})\n".format(tx))
								is_STATUS[tx] = True
								n_STATUS[tx] = 0
			
			elif is_CRC[tx]:
				crc_word = temp[6:8] + temp[4:6] + temp[2:4] + temp[0:2]		## CRC value (32-bit)
				print("CRC WORD: {} (sector {})".format(crc_word, tx))
				k_file.write("CRC WORD: {} (sector {})\n".format(crc_word, tx))
				out_file.write("CRC WORD: {} (sector {})\n".format(crc_word, tx))
				is_CRC[tx] = False
			elif is_FRAME[tx]:
				framecount = temp[6:8] + temp[4:6] + temp[2:4] + temp[0:2]		## frame number (16-bit)
				print("FRAME COUNT: 0x{} (sector {})".format(framecount, tx))
				k_file.write("FRAME COUNT: 0x{} (sector {})\n".format(framecount, tx))
				out_file.write("FRAME COUNT: 0x{} (sector {})\n".format(framecount, tx))
				is_FRAME[tx] = False
			elif is_STATUS[tx]:
				status_word = temp[6:8] + temp[4:6] + temp[2:4] + temp[0:2]		## status word (32-bit)
				t = bin( int(status_word, 16) )[2:].zfill(32)

				if n_STATUS[tx] < 8:
					#print(t)
					pixel_col = int( t[0:3] , 2 )
					pixel_id = int( t[3:6] , 2 )
					lost_ev = int( t[6:12] , 2 )
					lost_1 = int( t[12:16] , 2 )
					lost_2 = int( t[16:20] , 2 )
					lost_3 = int( t[20:24] , 2 )
					lost_4 = int( t[24:28] , 2 )
					seu = int( t[28:32] , 2 )
					print("STATUS WORD Sector {}: COL = {}, ID = {}, PIXEL = {}, EV_LOST = {}, TDC1 = {}, TDC2 = {}, TDC3 = {}, TDC4 = {}, SEU = {}".format(tx, pixel_col, pixel_id, pixel_col*4+pixel_id, lost_ev, lost_1, lost_2, lost_3, lost_3, seu))
					k_file.write("STATUS WORD Sector {}: COL = {}, ID = {}, PIXEL = {}, EV_LOST = {}, TDC1 = {}, TDC2 = {}, TDC3 = {}, TDC4 = {}, SEU = {}\n".format(tx, pixel_col, pixel_id, pixel_col*4+pixel_id, lost_ev, lost_1, lost_2, lost_3, lost_3, seu))
					out_file.write("STATUS WORD Sector {}: COL = {}, ID = {}, PIXEL = {}, EV_LOST = {}, TDC1 = {}, TDC2 = {}, TDC3 = {}, TDC4 = {}, SEU = {}\n".format(tx, pixel_col, pixel_id, pixel_col*4+pixel_id, lost_ev, lost_1, lost_2, lost_3, lost_3, seu))

					if lost_ev != 0:
						print(temp)
						print("EVENT LOST!!!")						
						#sys.exit()
				elif n_STATUS[tx] == 8:
					#print(t)
					EoC_out_FIFO_loss = int( t[0:8], 2 )
					EoC_in_FIFO_loss = int( t[8:16], 2 )
					event_count = int( t[16:32], 2 )
					print( "STATUS WORD Sector {}: EoC_out_FIFO_loss = {}, EoC_in_FIFO_loss = {}, event_count = {}".format(tx, EoC_out_FIFO_loss, EoC_in_FIFO_loss, event_count) )
					k_file.write( "STATUS WORD Sector {}: EoC_out_FIFO_loss = {}, EoC_in_FIFO_loss = {}, event_count = {}\n".format(tx, EoC_out_FIFO_loss, EoC_in_FIFO_loss, event_count) )
					out_file.write( "STATUS WORD Sector {}: EoC_out_FIFO_loss = {}, EoC_in_FIFO_loss = {}, event_count = {}\n".format(tx, EoC_out_FIFO_loss, EoC_in_FIFO_loss, event_count) )
					if EoC_out_FIFO_loss != 0 or EoC_in_FIFO_loss != 0:
						print("************************")
						print("************************")
						print("**                    **")
						print("**  EoC FIFO loss!!!  **")
						print("**                    **")
						print("************************")
						print("************************")
						#sys.exit()

				#print("STATUS WORD ({}) = {} (sector {})".format(n_STATUS[tx], status_word, tx))
				#k_file.write("STATUS WORD ({}) = {} (sector {})\n".format(n_STATUS[tx], status_word, tx))
				#out_file.write("STATUS WORD ({}) = {} (sector {})\n".format(n_STATUS[tx], status_word, tx))

				n_STATUS[tx] += 1
				if n_STATUS[tx] == 9:									## 9 status words for each sector (one per pixel + one for EoC)
					#print("END of STATUS WORDS.")
					is_STATUS[tx] = False


			########################################################################################################################################
			########################################################################################################################################


			elif check != 0 or zeros != 0:										## error
				print("PACKET NUMBER = {}".format(packet_number) )
				print("CHECK ERROR!!!")
				print("CHECK = {}".format(check))
				print("ZEROS = {}".format(zeros))
				sys.exit()
			else:																## event-word
				#print("TX = {}\n".format(tx))

				#data = bin( int( temp , 16) )[8:].zfill(32)
				bin_data = bin( int( temp[0:8] , 16) )[2:].zfill(32)
				
				#print(len(bin_data))
				#print(bin_data)
				#print(bin_data[15:16] + data[0:8])
				col_id = int(bin_data[24:27], 2)						# 3-bit
				if int(col_id/2) != tx:
					print("************************")
					print("************************")
					print("**                    **")
					print("**  TX ERROR!!! ({})  **".format(tx))
					print("**                    **")
					print("************************")
					print("************************")
					#sys.exit()
				
				else:
					d = dict()

					pix_id = int(bin_data[27:30], 2)					# 3-bit
					pixel_number = col_id*4 + pix_id
					#pixel_hits.append(pixel_number)
					tdc_id = int(bin_data[30:32], 2)					# 2-bit
					Tcoarse = int(bin_data[16:24] + bin_data[8:15], 2)
					Tfine = int(bin_data[15:16] + bin_data[0:8], 2)
					
					d = { "packet": packet_number, "pixel": pixel_number, "tdc": tdc_id, "Tcoarse": Tcoarse, "Tfine": Tfine }
					row_list.append(d)

					if is_txt:
						out_file.write("packet: {}, pixel: {}, tdc: {}, Tcoarse: {}, Tfine: {}\n".format(packet_number, pixel_number, tdc_id, Tcoarse, Tfine))
					

		#byte = f.read(1)
		#n += 1


# end decode

##########################################################################
##########################################################################


print("\n\n\nRead complete.\n{} packets read.\n".format(packet_number) )

if is_txt:
	out_file.close()
	k_file.close()


#n_entries = len(pixel_hits)
#print("Total number of hits = {}\n".format(n_entries))

#df = pd.DataFrame(data = None, index = None, columns = ["pixel_number", "tdc_id", "Tcoarse", "Tfine"])
df = pd.DataFrame(row_list, columns = ["packet", "pixel", "tdc", "Tcoarse", "Tfine"])
print("Saving dataframe to pickle...")
df.to_pickle("{}RUN_{}_pickle.gz".format(output_path, RUN), compression="gzip")
print("Saving done.")

n_col = len(df.columns)									## number of columns
n_row = int(df.size / n_col)							## number of entries (=hits)
print("Total number of hits = {}\n".format(n_row))



if is_plot:


	pix_num = 0


	fig, axs = plt.subplots(2,2, figsize=(16,9), sharex=False)
	binning = np.arange(50, 250, 1)
	plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95, wspace=0.2, hspace=0.2)

	df[(df.tdc==0) & (df.pixel==pix_num)].Tfine.plot.hist(bins=binning, color='red', alpha=0.8, ax=axs[0][0])
	axs[0][0].set_xlabel('Tfine [digits]')
	axs[0][0].grid()

	df[(df.tdc==1) & (df.pixel==pix_num)].Tfine.plot.hist(bins=binning, color='blue', alpha=0.8, ax=axs[0][1])
	axs[0][1].set_xlabel('Tfine [digits]')
	axs[0][1].grid()

	df[(df.tdc==2) & (df.pixel==pix_num)].Tfine.plot.hist(bins=binning, color='green', alpha=0.8, ax=axs[1][0])
	axs[1][0].set_xlabel('Tfine [digits]')
	axs[1][0].grid()

	#df[(df.tdc==3) & (df.pixel==pix_num) & (df.packet>40000)].T_fine.plot.hist(bins=binning, color='yellow', alpha=0.8, ax=axs[1][1])
	df[(df.tdc==3) & (df.pixel==pix_num)].Tfine.plot.hist(bins=binning, color='yellow', alpha=0.8, ax=axs[1][1])
	axs[1][1].set_xlabel('Tfine [digits]')
	axs[1][1].grid()

	plt.setp(axs[0][0], title="TFine (Pixel {}, TDC 0)".format(pix_num))
	plt.setp(axs[0][1], title="TFine (Pixel {}, TDC 1)".format(pix_num))
	plt.setp(axs[1][0], title="TFine (Pixel {}, TDC 2)".format(pix_num))
	plt.setp(axs[1][1], title="TFine (Pixel {}, TDC 3)".format(pix_num))

	plt.show()


	###############################################################################
	###############################################################################


	binning = np.arange(0, 35000, 10)
	df[(df.pixel==pix_num)].Tcoarse.plot.hist(bins=binning, color='blue', alpha=0.8)
	plt.title("TCoarse (Pixel {})".format(pix_num))
	plt.xlabel('Tcoarse [digits]')
	plt.ylabel('N')
	plt.grid()

	plt.show()



	###############################################################################
	###############################################################################



	##################################################################
	##################################################################

	plt.figure(1, figsize=(12,8))
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

	plt.figure(2, figsize=(10,7))
	x = range(0, len(err))
	plt.plot(x, err, 'r--')
	plt.title("TFine = 0 occurence on TDC n.1")
	plt.xlabel("row")
	plt.ylabel("TFine error")
	plt.grid()
	plt.show()

	##################################################################
	##################################################################


