# -*- coding: utf-8 -*-

import platform, serial, serial.tools.list_ports, time
from ctypes import c_ushort


__author__    = 'Kazuyuki TAKASE'
__author__    = 'Yugo KAJIWARA'
__copyright__ = 'PLEN Project Company Ltd., and all authors.'
__license__   = 'The MIT License'


class Core:
	def __init__(self, device_map):
		self._serial     = None
		self._DEVICE_MAP = device_map
		self._values     = [ 0 for x in range(24) ]
		self.debugmode=1

	def serial_write(self,cmd,fun_name=""):
		if self.debugmode==1:
			print("%s cmd=%s" %(fun_name, cmd))
			if not isinstance(cmd, basestring):
				str1=""
				for i in cmd:
					str1=str1+chr(i)
				print("String format=%s" %(str1))
		self._serial.write(cmd)
	def debug(self,print_str):
		if self.debugmode==1:	
			print(print_str)
	def output(self, device, value):
		if self._serial == None:
			return False

		cmd = "$AD%02x%03x" % (self._DEVICE_MAP[device], c_ushort(value).value)
		self.serial_write(cmd,"output")

		return True

	def play(self, slot):
		if self._serial == None:
			return False

		cmd = "$PM%02x" % slot
		#print("cmd=" + cmd)
		self.serial_write(cmd,"play")

		return True

	def stop(self):
		if self._serial == None:
			return False

		cmd = "$SM"
		self.serial_write(cmd,"stop")

		return True

	def install(self, json):
		if self._serial == None:
			return False

		# コマンドの指定
		cmd = ">IN"

		# スロット番号の指定
		self.debug("slot=%02x"%(json["slot"]))
		cmd += "%02x" % (json["slot"])
		
		# モーション名の指定
		if len(json["name"]) < 20:
			cmd += json["name"].ljust(20)
		else:
			cmd += json["name"][:19]
		self.debug("name=%s"%(json["name"]))
		# 制御機能の指定
		if (len(json["codes"]) != 0):
			for code in json["codes"]:
				if (code["func"] == "loop"):
					cmd += "01%02x%02x" % (code["args"][0], code["args"][1])
					self.debug("func_loop=01%02x%02x"%(code["args"][0], code["args"][1]))
					break

				if (code["func"] == "jump"):
					cmd += "02%02x00" % (code["args"][0])
					self.debug("func_jump=02%02x00" % (code["args"][0]))
					break
		else:
			cmd += "000000"

		# フレーム数の指定
		cmd += "%02x" % (len(json["frames"]))
		self.debug("frames=%02x" % (len(json["frames"])))
		# フレーム構成要素の指定
		for frame in json["frames"]:
			# 遷移時間の指定
			cmd += "%04x" % (frame["transition_time_ms"])
			self.debug("transition_time_ms=%04x" % (frame["transition_time_ms"]))
			for output in frame["outputs"]:
				self._values[self._DEVICE_MAP[output["device"]]] = c_ushort(output["value"]).value

			for value in self._values:
				cmd += "%04x" % value
				#self.debug("per frame values=%04x" % value)

		# Divide command length by payload size.
		block   = len(cmd) // 20
		surplus = len(cmd) % 20

		self.debug("cmd buffer(not sending): %s" %(cmd))
		for index in range(block):
			self.serial_write(map(ord, cmd[20 * index: 20 * (index + 1)]),"install(index)")
			time.sleep(0.01)

		self.serial_write(map(ord, cmd[-surplus:]),"install")
		time.sleep(0.01)

		return True

	def connect(self):
		com = None

		for device in list(serial.tools.list_ports.comports()):
			if 'Arduino Micro' in device[1]:
				com = device[0]

		# Fix for old version mac.
		if (  ( (com == None)
			and (platform.system() == 'Darwin') )
		):
			for device in list(serial.tools.list_ports.comports()):
				if ( ( ('/dev/tty.usbmodem'  in device[0])
					or ('/dev/tty.usbserial' in device[0])
					or ('/dev/cu.usbmodem'   in device[0])
					or ('/dev/cu.usbserial'  in device[0]) )
				):
					try:
						openable = serial.Serial(port = device[0])
						openable.close()

						com = device[0]

					except serial.SerialException:
						pass

		if com == None:
			return False

		self.disconnect()

		if self._serial == None:
			self._serial = serial.Serial(port = com, baudrate = 2000000, timeout = 1)
			self._serial.flushInput()
			self._serial.flushOutput()

		return True

	def disconnect(self):
		if self._serial == None:
			return False

		self._serial.close()
		self._serial = None

		return True
