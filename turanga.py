#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Image
import sys
import os
import random
import datetime
import time
from fractions import gcd

class TurangaFormatFile:

	#lint:disable
	def __init__(self, filename, key):
		self.key = key
		self.filename = filename

	def w(self, content):
		f = open("." + self.filename + ".trg","w")
	
		header  = "turangakeyfile"
		version = "1.0"
		date    = datetime.datetime.now().strftime("%d-%m-%Y")
		time    = datetime.datetime.now().strftime('%H:%M')
		
		turangaFile = header + version + date + time + content
		
		build = ""
		
		for byte in turangaFile:
			build += str(ord(byte)).zfill(3)
			
		f.write(build)
		f.close()
		
		cfile = TurangaTextCryp("." + self.filename + ".trg", self.key)
		cf = open(self.filename + ".crg","w")
		cf.write(cfile.cryp())
		
		print("\033[0;36m [i] " + self.filename + ".crg saved :)\033[0m")
		cf.close()
		os.remove("." + self.filename + ".trg")
		
	def r(self):
		dt = TurangaTextCryp(self.filename + ".crg", self.key)
		r = dt.decryp()
		
		tb = str()
		b  = str()
		content = str()
		bytescontent = str()
		
		header, version, date, time = "", "", "", ""
		
		bytecount  = 1
		tbytecount = 1
		for tbyte in r:
			tb += tbyte
			if tbytecount == 3:
			    try:
				b += chr(int(tb))
				if bytecount == 14:
					header = b
					if not header == "turangakeyfile":
						print (" [!] Error, archivo no valido!")
						sys.exit()
					b = str()
				if bytecount == 17:
					version = b
					b = str()
				if bytecount == 27:
					date = b
					b = str()
				if bytecount == 32:
					time = b
					b = str()
				if bytecount > 32:
					content += b
					bytescontent += str(ord(b))
					b = str()
				
				bytecount = bytecount + 1
				tb = str()
				tbytecount = 0
			    except:
			      print "\033[0;36m [!] Error al procesar la llave, quiza la clave sea incorrecta.\033[0m"
			      sys.exit()

			tbytecount = tbytecount + 1
		
		print("\n\033[0;36m [*] Turanga Key File - version " + version + "\033[0m")
		print("          Date:     " + date + " at " + time)
		print("          Size:     " + str(bytecount) + " bytes")
		print("          ContSize: " + str(bytecount - 33).zfill(2) + " bytes")
		print(" ==============================================================")
		print("\n  " + str(bytescontent) + "\n")
		print(" ==============================================================\n")
		
		return str(content)

class TurangaImageCryp:

	def __init__(self, pathInput, pathOutput, key):
		
		self.pathInput  = pathInput
		self.pathOutput = pathOutput
		self.key = key
		
		self.imageObject = Image.open(self.pathInput)
		self.imagePixels = self.imageObject.load()
		
		self.outputDataObject = Image.new("RGB",self.imageObject.size, "white")
		self.outputDataPixels = self.outputDataObject.load()
		
	def inv_mult(self,a):
	 	n = 256
 		if(gcd(a,n)!=1):
  			print(" [*] Error, ")
 		else:
  			for i in range(1,n) :
				if( ( a*i-1 )%n == 0 ):
					return i
	
	def genKey(self):
		# creates a 5000 random character string to encrypt image
		print (" [*] Generating key ...")

		pool    = "13579"
		key     = str()
		
		for i in range(0, 20):
			key  += pool[random.randrange(len(pool) - 1)]
		
		return key
		
	def cryp(self):
	
		self.turangafile = TurangaFormatFile(self.pathOutput, self.key)
	
		self.internalkey     = self.genKey()
		self.internalkeysize = len(self.internalkey)
		self.externalkey = str()
		
		print(" [*] Image for crypt: \033[0;36m" + self.pathInput + "\033[0m")
		print("\n [i] Working ... please wait")
		
		k, kc = 0, 0 # counter for index key
		bytesCount = 0 #bytes counter

		# image pixel by pixel
		for x in range(0, self.imageObject.size[0]):
			for y in range(0, self.imageObject.size[1]):
				RGB = self.imagePixels[x,y]
				newRGB = ()
				
				colorcount = 1
				for color in RGB:
					#reset key index if it reaches its limit
					if k >= self.internalkeysize - 1:
						k = 0
					# the new byte value will be given by the original value
					# minus the value of 2 key digits
					a = int(self.internalkey[k] + self.internalkey[k + 1])
					
					inv = self.inv_mult(a)
					
					result = (color * a) % 256
					
					if kc == 0:
						print (" [*] Building a decrypt key ...\n")
					if kc <= 19:
						print ("     color : " + str(color) + " key : " + str(a) + " inv :\033[0;36m " + str(inv).zfill(3) + "\033[0m r : " + str(result).zfill(3))
						self.externalkey += chr(inv)
					if kc == 20:
						print ("\n [i] Build decrypt key done! :)")
						self.turangafile.w(self.externalkey)
						print("\n [*] Working please wait ...")

					k = k + 1	# increases the index key
					kc = kc +1
					colorcount = colorcount + 1
					# set de new byte
					newRGB = newRGB + (result, )
					
				bytesCount = bytesCount + 1 # increases the bytes count
				self.outputDataPixels[x,y] = newRGB # save the new pixel
		# save the new image
		self.outputDataObject.save(self.pathOutput + ".png", "PNG")
		
		print ("\n\033[0;36m [*] Done! \033[0m")
		print (" [i] " + str(bytesCount) + " bytes crypted in \033[0;36m" + self.pathOutput + ".png\033[0m\n")
		
	def decryp(self):
		# load the key file
		filename = self.pathInput.split(".")
		self.turangafile = TurangaFormatFile(filename[0], self.key)
		print(" [i] Loading key file(\033[0;36m" + filename[0] + ".crg\033[0m) ...")
		
		self.internalkey     = self.turangafile.r()
		self.internalkeysize = len(self.internalkey)
		
		print(" [i] Working ... please wait")
		
		k = 0
		byteCount = 0
		p = 0
		# image pixel by pixel
		for x in range(0, self.imageObject.size[0]):
			for y in range(0, self.imageObject.size[1]):

				RGB = self.imagePixels[x,y]
				newRGB = ()

				for color in RGB:
					if k >= (self.internalkeysize - 1):
						k = 0
					# reverse process to the previous
					result = (ord(self.internalkey[k]) * color) % 256
					
					k = k + 1
					p = p + 1
					newRGB = newRGB + (result, )
					
				byteCount = byteCount + 1
				self.outputDataPixels[x,y] = newRGB
			
		self.outputDataObject.save(self.pathOutput + ".png", "PNG")
		
		print ("\n\033[0;36m [*] Done! \033[0m")
		print (" [i] " + str(byteCount) + " bytes decrypted in \033[0;36m" + self.pathOutput + ".png\033[0m\n")

# ================================================================================ TuranagaImageCryp ends

class TurangaUnestegData:

	def __init__(self, pathInput, pathOutput):
		
		self.pathInput  = pathInput
		self.pathOutput = pathOutput
		
		self.imageObject = Image.open(self.pathInput)
		self.imagePixels = self.imageObject.load()
		
	def readImageBits(self):
		# image bit by bit
		for x in range(0, self.imageObject.size[0]):
			for y in range(0, self.imageObject.size[1]):
				RGB = self.imagePixels[x,y]
				for color in RGB:
					yield bin(color)[-1:] # just take the last byte
	
	def unesteg(self):
		bitCount  = 0
		byteCount = 0
		byte = str()
		data = str()
		maxeof = 4294967295           # maximum file size
		bytes = self.readImageBits()
		
		for bit in bytes:
			byte += bit
			bitCount = bitCount + 1
			
			# builds a byte
			if bitCount == 8:
				byteCount = byteCount + 1
				data += byte
				
				# the first 4 bytes, which is the information about the size of the hidden file
				if byteCount == 4:
					size = data
					print("[i] Size of the hidden file: " + str(int(size, 2)) + " bytes")
					maxeof = int(size ,2) + 7 # 7 bytes extra data :p
					data = str() # reset
				
				# when we got at 4 bytes, we reset, so to get to the seventh, we have 3 bytes,
				# which is the information format.
				if byteCount == 7:
					a = chr(int(data[:8],2))
					b = chr(int(data[8:16],2))
					c = chr(int(data[16:24],2))
					fileFormat = a + b + c
					print("[i] Format of the hidden file: " + fileFormat)
					outputfile = open(self.pathOutput + "." + fileFormat , "wb") # open a file for writing with the name and format
				# from the eighth byte read original data file
				if byteCount > 7:
					outputfile.write(chr(int(byte,2)))
				
				byte     = str()
				bitCount = 0
				
				# ends to cover the file size
				if byteCount == maxeof:
					break
					
		print ("\n[*] Done :)")
		print ("========================================================")
		print (str(byteCount - 7) + " bytes writed on file " + self.pathOutput)
		
		outputfile.close()
		
# ================================================================== UnestegData ends

class TurangaEstegData:

	def __init__(self, pathData, pathImage, pathOutput, formatFile):
		
		self.pathData   = pathData
		self.pathImage  = pathImage
		self.pathOutput = pathOutput
		self.formatFile = formatFile
		
		# the file where they will hide
		self.imageObject = Image.open(self.pathImage)
		self.imagePixels = self.imageObject.load()
		
		# the file to hide
		self.data = open(self.pathData, "rb")
		
		# output file
		self.outputDataObject = Image.new("RGB", self.imageObject.size, "white")
		self.outputDataPixels = self.outputDataObject.load()
	
	def readDataBits(self):
		# first 32 bits that represent the size of the hidden file
		dataSize = os.fstat(self.data.fileno()).st_size
		for bit in bin(dataSize)[2:].zfill(32):
			yield bit
		
		# 54 bits that determine the format
		for char in self.formatFile:
			byte = bin( ord(char) )[2:].zfill(8)
			for bit in byte:
				yield bit
		# finally the bits of the file to hide
		while True:
			char = self.data.read(1)
			if not char:
				break
			else:
				byte = bin( ord(char) )[2:].zfill(8)
				for bit in byte:
					yield bit
					
	def esteg(self):
		# instance of the bits to iterate
		inBytes   = self.readDataBits()
		bitsCount = 0;
		
		print("\n[*] Working...")
		
		# new image pixel by pixel
		for x in range(0, self.imageObject.size[0]):
			for y in range(0, self.imageObject.size[1]):
				
				RGB    = self.imagePixels[x,y]
				newRGB = ()
				
				for color in RGB:
					try:
						# the new byte will come given by the original bits except de last bit
						# where we will place one of file to hide
						newRGB    = newRGB + ( int( bin(color)[:-1]+inBytes.next() ,2), )
						bitsCount = bitsCount + 1
					except StopIteration:
						# if there is no bits to hide, send the original byte
						newRGB = RGB + (color, )
				try:
				  self.outputDataPixels[x,y] = newRGB
				except:
				  print "[!] Algo salio mal, asegurate de que la imagen sea bmp o jpg"
				  sys.exit()
		# save the new image	
		self.outputDataObject.save(self.pathOutput + ".png")
		
		print ("[*] Done!")
		print ("\n===================================================")
		print ("data:   " + self.pathData)
		print ("image:  " + self.pathImage)
		print ("output: " + self.pathOutput + ".png")
		print ("\nhide:    " + str(bitsCount) + " bits")
		print ("56 bits extra in the original file (file size and format)")
		
# =================================================================================== EstegData ends

class TurangaTextCryp:

	def __init__(self, pathFile, key):
		
		self.pathFile   = pathFile
		#self.pathOutput = pathOutput
		self.key        = key
		self.keysize    = len(key) - 1
		self.filesize   = 0
	
	def cryp(self):
		# Read fileo
		readFile = open(self.pathFile)
		data = readFile.read()
		# set the output file
		#outputfile = open(self.pathOutput + ".crg", "wb")
		output = ""
		
		j      = 0 # key index counter
		bCount = 0 # bytes counter

		# file byte by byte
		for i in range(0, len(data)):
			# reset the key index when this got to the limit
			if j >= self.keysize:
				j = 0
			
			# the new byte is equal to the sum of the ASCII values ​​of the original byte plus the key byte
			result = ord(data[i]) + ord(self.key[j])
			
			# only values betwen 0 and 255
			if result > 255:
				result = 0
			
			# write the new byte
			#outputfile.write(chr(result))
			output += chr(result)
			
			j = j + 1
			bCount = bCount + 1
		return "trg" + output
#		print ("\n [*] Done! ")
#		print (" [i] "str(bCount) + " bytes encrypted")
		
		#outputfile.close()
		
	def decryp(self):
                # reverse process to the previous
                readFile = open(self.pathFile)
                data = readFile.read()
                dataout = str()
		
                #outputfile = open(self.pathOutput + ".txt", "wb")
		
                j      = 0
                bCount = 0

                if data[0:3] == "trg":
                    for i in range(3, len(data)):
                        if j >= self.keysize:
                            j = 0

                        result = ord(data[i]) - ord(self.key[j])
                        if result < 0:
                            result = 255
				
                        dataout += chr(result)
			
                        j = j + 1
                        bCount = bCount + 1
			
                    #outputfile.write(dataout.rstrip())
                    return dataout.rstrip()
                else:
                     return False
		
		#outputfile.close()
# ============================================================================== TurangaTextCryp ends

class TurangaConvert:
	
	def __init__(self, pathFile, outputName, fileformat):
		self.pathFile     = pathFile
		self.outputName   = outputName
		self.fileformat   = fileformat
	
	def convert(self):
		if self.fileformat == "jpg":
			if os.path.exists(self.pathFile):
				new = Image.open(self.pathFile)
				new.save(self.outputName + ".bmp","BMP")
				print ("[*] Sucesful convertion!\n output: " + self.outputName + ".bmp")
			else:
				print ("[!] Error, file " + self.outputName + "don't exist!")
				sys.exit()
		elif self.fileformat == "png":
			if os.path.exists(self.pathFile):
				new = Image.open(self.pathFile)
				r, g, b, a = new.split()
				new = Image.merge("RGB", (r, g, b))
				new.save(self.outputName + ".bmp","BMP")
				print ("[*] Sucesful convertion!\n output: " + self.outputName + ".bmp")
			else:
				print ("[!] Error, file " + self.outputName + "don't exist!")
				sys.exit()
				

				
				
def imgdecryp_recursive():
  print " [*]Reading list ..."
  f = open(sys.argv[3])
  data = f.read()
  data = data.rstrip()
  list = data.split("\n")
  n = len(list)
  c = 1
  key = raw_input(" [*] Clave de cifrado: ")
  for img in list:
      name = img.split(".")
      name = name[0] + "r"
      print "\n\033[0;36m [*] Decrypting files [" + str(c) + "/" + str(n) + "]\033[0m\n"
      imgc = TurangaImageCryp(img, name, key)
      imgc.decryp()
      c += 1
  o = raw_input(" [*] Eliminar archivos cifrados?[s/n] ")
  if o == "s":
    for img in list:
      key = img.split(".")
      key = key[0] + ".crg"
      os.remove(img)
      os.remove(key)
    os.remove(sys.argv[3])
  print " [*] TRG Done"
				
				
def imgcryp_recursive():
  print " [*]Reading list ..."
  f = open(sys.argv[3])
  data = f.read()
  data = data.rstrip()
  list = data.split("\n")
  n = len(list)
  c = 1
  o = raw_input(" [i] Cifrar " + str(n) + " archivos?[s/n] ")
  if o == "s":
    key = raw_input(" [*] Clave de cifrado: ")
    dlist = open(sys.argv[3] + "_rev","wb")
    for img in list:
      name = img.split(".")
      name = name[0] + "_c"
      print "\n\033[0;36m [*] Crypting files [" + str(c) + "/" + str(n) + "]\033[0m\n"
      imgc = TurangaImageCryp(img, name, key)
      imgc.cryp()
      dlist.write(name + ".png\n")
      c += 1

    dlist.close()
    print "\n [i] Se cifraron correctamente todos los archivos"
    print " [i] Para decifrarlos automaticamente ejecute '<turanga> -di -l " + sys.argv[3] + "_rev'\n"

    o = raw_input(" [!] Eliminar originales?[s/n] ")
    if o == "s":
      for img in list:
	os.remove(img)

      os.remove(sys.argv[3])

      print " [i] Archivos originales eliminados"

def show_info(logo):
	if logo == 0:
		print"""\033[0;36m
		▄▄▄█████▓ █    ██  ██▀███   ▄▄▄       ███▄    █   ▄████  ▄▄▄
		▓  ██▒ ▓▒ ██  ▓██▒▓██ ▒ ██▒▒████▄     ██ ▀█   █  ██▒ ▀█▒▒████▄
		▒ ▓██░ ▒░▓██  ▒██░▓██ ░▄█ ▒▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░▒██  ▀█▄
		░ ▓██▓ ░ ▓▓█  ░██░▒██▀▀█▄  ░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓░██▄▄▄▄██
		  ▒██▒ ░ ▒▒█████▓ ░██▓ ▒██▒ ▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒ ▓█   ▓██▒
		  ▒ ░░   ░▒▓▒ ▒ ▒ ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒  ▒▒   ▓▒█░
		    ░    ░░▒░ ░ ░   ░▒ ░ ▒░  ▒   ▒▒ ░░ ░░   ░ ▒░  ░   ░   ▒   ▒▒ ░
		  ░       ░░░ ░ ░   ░░   ░   ░   ▒      ░   ░ ░ ░ ░   ░   ░   ▒
		            ░        ░           ░  ░         ░       ░       ░  ░
		\033[0m"""
	elif logo == 1:
		print"""\033[0;36m
		┌┬┐┬ ┬┬─┐┌─┐┌┐┌┌─┐┌─┐
		 │ │ │├┬┘├─┤││││ ┬├─┤
		 ┴ └─┘┴└─┴ ┴┘└┘└─┘┴ ┴
		\033[0m"""
	elif logo == 2:
		print"""\033[0;36m
		   ▄▄▄▄▀ ▄   █▄▄▄▄ ██      ▄     ▄▀  ██
		▀▀▀ █     █  █  ▄▀ █ █      █  ▄▀    █ █
		    █  █   █ █▀▀▌  █▄▄█ ██   █ █ ▀▄  █▄▄█
		   █   █   █ █  █  █  █ █ █  █ █   █ █  █
		  ▀    █▄ ▄█   █      █ █  █ █  ███     █
		        ▀▀▀   ▀      █  █   ██         █
		                    ▀                 ▀
		\033[0m"""
	elif logo == 3:
		print"""\033[0;36m
 ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀▀▀▀█░█▀▀▀▀ ▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌
     ▐░▌     ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌▐░▌    ▐░▌▐░▌          ▐░▌       ▐░▌
     ▐░▌     ▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌ ▐░▌   ▐░▌▐░▌ ▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌
     ▐░▌     ▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌  ▐░▌  ▐░▌▐░▌▐░░░░░░░░▌▐░░░░░░░░░░░▌
     ▐░▌     ▐░▌       ▐░▌▐░█▀▀▀▀█░█▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░▌   ▐░▌ ▐░▌▐░▌ ▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌
     ▐░▌     ▐░▌       ▐░▌▐░▌     ▐░▌  ▐░▌       ▐░▌▐░▌    ▐░▌▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
     ▐░▌     ▐░█▄▄▄▄▄▄▄█░▌▐░▌      ▐░▌ ▐░▌       ▐░▌▐░▌     ▐░▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌
     ▐░▌     ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌
      ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀         ▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀
		\033[0m"""
	else:
		print"""\033[0;36m
		▄▄▄▄▄▄• ▄▌▄▄▄   ▄▄▄·  ▐ ▄  ▄▄ •  ▄▄▄·
		•██  █▪██▌▀▄ █·▐█ ▀█ •█▌▐█▐█ ▀ ▪▐█ ▀█
		 ▐█.▪█▌▐█▌▐▀▀▄ ▄█▀▀█ ▐█▐▐▌▄█ ▀█▄▄█▀▀█
		 ▐█▌·▐█▄█▌▐█•█▌▐█ ▪▐▌██▐█▌▐█▄▪▐█▐█ ▪▐▌
		 ▀▀▀  ▀▀▀ .▀  ▀ ▀  ▀ ▀▀ █▪·▀▀▀▀  ▀  ▀
		\033[0m"""
	
	print """
	Turanga is a tool written in python oriented cryptography and / or steganography.
				
	@autor	 :  eduardo <ms7rbeta@gmail.com>
	@license :  GNU/GPL v3
	@version :  2.0
		  """
def show_help():
	show_info(random.randrange(4))
	print ('\n   Usage:')
	print ('   =========================================================================================')
	print ('   Hide   a File in   a Image :\033[0;36m <turaga> -es <FileToHide>    <Image>        <NameToOutput> \033[0m')
	print ('   Unhide a File from a Image :\033[0;36m <turaga> -un <ImageWithData> <NameToOutput> \033[0m')
	print ('   Cryp   a TextFile          :\033[0;36m <turaga> -ct <File>          <key> \033[0m')
	print ('   Decryp a TextFile          :\033[0;36m <turaga> -dt <CrypedFile>    <key> \033[0m')
	print ('   Cryp   a Image             :\033[0;36m <turaga> -ci <Image>         <NameToOutput> \033[0m')
	print ('   Decryp a Image             :\033[0;36m <turaga> -di <CrypedImage>   <NameToOutput> \033[0m')
	print ('   Convert a file             :\033[0;36m <turaga> -cv <File>          <NameToOutput> <type>\033[0m')
	print ('   =========================================================================================\n')
	print ('   [Cifrar varias imagenes en un solo comando]')
	print ('\n       - Existe la manera de cifrar un grupo de imagenes de una sola vez, para esto')
	print ('       es necasario crear una lista con los nombres de las imagenes que deseamos')
	print ('       podemos generar esta lista desde la linea de comandos facilmente:')
	print ('\n       Linux:')
	print ('                  \033[0;36m ls *.jpg > img_list \033[0m')
	print ('       Windows:')
	print ('                  \033[0;36m dir *.jpg>img_list.txt \033[0m')
	print ('\n       y con esto tendremos un fichero que contiene los nombres de las imagenes que')
	print ('       se quieren cifrar, ahora solo queda ejecutar:')
	print ('\n        \033[0;36m <turanga> -ci --list img_list \033[0m')
	print ('                       ó')
	print ('        \033[0;36m <turanga> -ci --list img_list.txt \033[0m')
	print ('\n       Al terminar el cifrado (toma en cuenta que puede tardar) genera una lista')
	print ('       que se usa para decifrar el grupo de imagenes y se hace de la siguiente manera:')
	print ('\n        \033[0;36m <turanga> -di --list img_list_rev \033[0m')

program_version = "Turanga 2.5 by ms7r"
	
if __name__ == "__main__":
    try:
	if sys.argv[1] == '--esteg' or sys.argv[1] == '-es':
		
		a = sys.argv[2].split(".")
		
		formatFile = a[1]
		
		sg = TurangaEstegData(sys.argv[2], sys.argv[3], sys.argv[4], formatFile)
		sg.esteg()
		
	elif sys.argv[1] == '--unesteg' or sys.argv[1] == '-un':
		
		un = TurangaUnestegData(sys.argv[2], sys.argv[3])
		un.unesteg()
		
	elif sys.argv[1] == '--cryptext' or sys.argv[1] == '-ct':
		un = TurangaTextCryp(sys.argv[2], sys.argv[3])
		print un.cryp()
		
	elif sys.argv[1] == '--decryptext' or sys.argv[1] == '-dt':
                  un = TurangaTextCryp(sys.argv[2], sys.argv[3])
                  result = un.decryp()
                  if result:
                    print result
                  else:
                    print " [*] El archivo no es un cifrado turanga!"
	
	elif sys.argv[1] == '--imgcryp' or sys.argv[1] == '-ci':
	    if sys.argv[2] == "-l" or sys.argv[2] == "--list":
		imgcryp_recursive()
	    else:
		key = raw_input(" [*] Clave de cifrado: ")
		imgc = TurangaImageCryp(sys.argv[2], sys.argv[3], key)
		imgc.cryp()

	
	elif sys.argv[1] == '--imgdecryp' or sys.argv[1] == '-di':
	    if sys.argv[2] == "-l" or sys.argv[2] == "--list":
		imgdecryp_recursive()
	    else:
		key = raw_input(" [*] Clave de cifrado: ")
		imgc = TurangaImageCryp(sys.argv[2], sys.argv[3], key)
		imgc.decryp()
		
		
	elif sys.argv[1] == '--convert' or sys.argv[1] == '-cv':
		a = sys.argv[2].split(".")
		
		formatFile = a[1]
		
		cv = TurangaConvert(sys.argv[2], sys.argv[3], formatFile)
		cv.convert()
	
	elif sys.argv[1] == "--version":
	    print program_version

	elif sys.argv[1] == "--help":
	  show_help()

	else:
	  print " [!] Sintax error, for help: <turanga> --help"
		
    except IndexError:
	print " [!] Type any option, for help: <turanga> --help"
