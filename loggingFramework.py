from datetime import datetime as dt
import traceback
from enum import Enum, auto
import atexit
import sys


class Logger:
	filename = "output.log"
	class LogLevel(Enum):
		MESSAGE = 0
		INFO = 1
		WARN = 2
		ERROR = 3
		WARNING = 2
		ERR = 3

	def __init__(self, logFile = "output.log", logWarnings = True, logErrors = True, logInfo = True, clearOldLog = True, *args, **kwargs):
		self.filename = logFile
		self.logWarnings = logWarnings
		self.logErrors = logErrors
		self.logInfos = logInfo
		self.loggerClosed = False
		openMode = "a+"
		if clearOldLog:
			openMode = "w"
		with open(logFile, openMode) as log:
			current = dt.now()
			log.write("{0}/{1}/{2} {3}:{4}:{5} - INFO: Logger Created\n".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2)))
		atexit.register(lambda: self.closeLogger())

	def logInfo(self, message, alsoPrint = False, *args, **kwargs):
		if not self.logInfos:
			return

		with open(self.filename, "a+") as log:
			current = dt.now()
			msg = "{0}/{1}/{2} {3}:{4}:{5} - INFO: {6}".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2), message)
			log.write(msg + "\n")
			if alsoPrint:
				print(msg)

	def logWarning(self, message, alsoPrint = True, *args, **kwargs):
		if not self.logWarnings:
			return
		
		with open(self.filename, "a+") as log:
			current = dt.now()
			msg = "{0}/{1}/{2} {3}:{4}:{5} - WARN: {6}".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2), message)
			log.write(msg + "\n")
			if alsoPrint:
				print(msg)

	def logError(self, message, alsoPrint = True, *args, **kwargs):
		if not self.logErrors:
			return
		
		with open(self.filename, "a+") as log:
			current = dt.now()
			msg = "{0}/{1}/{2} {3}:{4}:{5} - ERROR: {6}".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2), message)
			log.write(msg + "\n")
			if alsoPrint:
				print(msg, file=sys.stderr)

	def logException(self, exception: Exception, alsoPrint = True, *args, **kwargs):
		if not self.logErrors:
			return

		with open(self.filename, "a+") as log:
			current = dt.now()
			tb = "Exception Raised:\n"
			tb += "".join(traceback.format_tb(exception.__traceback__))
			tb += "{}: {}".format(repr(exception).split("(")[0], str(exception))

			msg = "{0}/{1}/{2} {3}:{4}:{5} - ERROR: {6}".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2), tb)

			log.write(msg + "\n")

			if alsoPrint:
				print(msg, file=sys.stderr)

	def writeToLog(self, message, logLevel: LogLevel = LogLevel.MESSAGE, alsoPrint = False, *args, **kwargs):
		if self.loggerClosed:
			return

		with open(self.filename, "a+") as log:
			current = dt.now()

			msg = "{0}/{1}/{2} {3}:{4}:{5} - {6}: {7}".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2), logLevel.name, message)

			log.write(msg + "\n")

			if alsoPrint:
				f = sys.stdout
				if logLevel == self.LogLevel.ERR or logLevel == self.LogLevel.ERROR:
					f = sys.stderr
				
				print(msg, file=f)
				
	def closeLogger(self):
		if self.loggerClosed:
			return
				
		with open(self.filename, "a+") as log:
			current = dt.now()
			self.logInfo = False
			self.logWarnings = False
			self.logErrors = False
			self.loggerClosed = True
			log.write("{0}/{1}/{2} {3}:{4}:{5} - INFO: Logger Closed\n".format(str(current.day).zfill(2), str(current.month).zfill(2), str(current.year).zfill(4), str(current.hour).zfill(2), str(current.minute).zfill(2), str(current.second).zfill(2)))
