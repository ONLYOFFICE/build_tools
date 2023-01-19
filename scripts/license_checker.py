import os
import datetime
import re
import enum

def getLicense(
		start: str = '/*',
		prefix: str = ' *',
		end: str = ' */' ,
		startYear:str = '2010',
		endYear:str = str(datetime.datetime.now().year)
	):
	"""Returns a valid license for any kind of comment prefix. Javascript and C++ by default."""
	license = f"""\
{start}
 {prefix} (c) Copyright Ascensio System SIA {startYear}-{endYear}
 {prefix}
 {prefix} This program is a free software product. You can redistribute it and/or
 {prefix} modify it under the terms of the GNU Affero General Public License (AGPL)
 {prefix} version 3 as published by the Free Software Foundation. In accordance with
 {prefix} Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect
 {prefix} that Ascensio System SIA expressly excludes the warranty of non-infringement
 {prefix} of any third-party rights.
 {prefix}
 {prefix} This program is distributed WITHOUT ANY WARRANTY; without even the implied
 {prefix} warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For
 {prefix} details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html
 {prefix}
 {prefix} You can contact Ascensio System SIA at 20A-12 Ernesta Birznieka-Upisha
 {prefix} street, Riga, Latvia, EU, LV-1050.
 {prefix}
 {prefix} The  interactive user interfaces in modified source and object code versions
 {prefix} of the Program must display Appropriate Legal Notices, as required under
 {prefix} Section 5 of the GNU AGPL version 3.
 {prefix}
 {prefix} Pursuant to Section 7(b) of the License you must retain the original Product
 {prefix} logo when distributing the program. Pursuant to Section 7(e) we decline to
 {prefix} grant you any rights under trademark law for use of our trademarks.
 {prefix}
 {prefix} All the Product's GUI elements, including illustrations and icon sets, as
 {prefix} well as technical writing content are licensed under the terms of the
 {prefix} Creative Commons Attribution-ShareAlike 4.0 International. See the License
 {prefix} terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode
 {prefix}
 {end}
"""
	return license

# Directory relative to which paths will be specified
PATH_TO_BASE_DIR = '../../'
os.chdir(PATH_TO_BASE_DIR)

class ErrorType(enum.Enum):
	INVALID_LICENSE = 0
	NO_LICENSE = 1
	UNKNOWN_ERROR = 2

class Error(object):
	def __init__(self, errorType: ErrorType) -> None:
		self._errorType = errorType
		self._errorMessages = {
		ErrorType.INVALID_LICENSE: 'The invalid license detected. Fix it',
		ErrorType.NO_LICENSE: 'The license was not found. Fix it',
		ErrorType.UNKNOWN_ERROR: 'Unknown error'
	}
	def getErrorType(self) -> ErrorType:
		return self._errorType
	def getErrorMessage(self) -> str:
		return self._errorMessages.get(self._errorType)
		
class Report(object):
	def __init__(self, pathToFile: str, error: Error) -> None:
		self._pathToFile = pathToFile
		self._error = error
	def getPathToFile(self) -> str:
		return self._pathToFile
	def getError(self) -> Error:
		return self._error
	def report(self) -> str:
		return f'{self._pathToFile}: {self._error.getErrorMessage()}'

class Config(object):
	"""
	License checker configuration.
	Attributes:
		dir: Directory to check.
		singleComm: characters that starts a single comment.
		fileExtensions: file extensions to check.
		startMultiComm: characters to start a multi-line comment.
		endMultiComm: characters to end a multi-line comment.
		prefix: prefix for multiline comments
		checkLines: number of lines to be checked at the beginning of the file.
		ignoreListDir: Ignored directories.
		ignoreListFile: Ignored files.
	"""
	def __init__(self,
		dir: str,
		singleComm: str,
		fileExtensions: list[str],
		startMultiComm: str = False,
		endMultiComm: str = False,
		prefix: str = '',
		checkLines: int = False, 
		ignoreListDir: list[str] = [],
		ignoreListFile: list[str] = []) -> None:

		self._dir = dir
		self._singleComm = singleComm
		self._fileExtensions = fileExtensions
		self._startMultiComm = startMultiComm
		self._endMultiComm = endMultiComm
		self._prefix = prefix
		self._checkLines = checkLines
		self._ignoreListDir = ignoreListDir
		self._ignoreListFile = ignoreListFile

	def getDir(self) -> str:
		return self._dir
	def getSingleComm(self) -> str:
		return self._singleComm
	def getFileExtensions(self) -> list[str]:
		return self._fileExtensions
	def getStartMultiComm(self) -> str:
		return self._startMultiComm
	def getEndMultiComm(self) -> str:
		return self._endMultiComm
	def getPrefix(self) -> str:
		return self._prefix
	def getCheckLines(self) -> int:
		return self._checkLines
	def getIgnoreListDir(self) -> list[str]:
		return self._ignoreListDir
	def getIgnoreListFile(self) -> list[str]:
		return self._ignoreListFile

class Checker(object):
	def __init__(self, config: Config) -> None:
		self._config = config
		self._reports: list[Report] = []
	def getReports(self):
		return self._reports
	def getLicense(self):
		if (not self._config.getStartMultiComm() and not self._config.getEndMultiComm()):
			license = getLicense(start='', prefix=self._config.getSingleComm(), end='')
		else:
			license = getLicense(start=self._config.getStartMultiComm(), prefix=self._config.getPrefix(), end=self._config.getEndMultiComm())
		return license
	def _checkLine(self, line: str, prefix: str) -> bool:
		"""Checks if a line has a prefix."""
		if (re.search(re.escape(prefix), line)):
			return True
		else:
			return False
	def findLicense(self, lines: list[str]) -> list[str]:
		"""Looks for consecutive comments in a list of strings."""
		result = []
		if (not self._config._startMultiComm and not self._config._endMultiComm):
			for line in lines:
				if (line == '\n'): continue
				if (self._checkLine(line=line, prefix=self._config.getSingleComm())):
					result.append(line)
				else:
					break
		else:
			isStarted = False
			for line in lines:
				if line == '\n': continue
				if (self._checkLine(line=line, prefix=self._config.getStartMultiComm())):
					result.append(line)
					isStarted = True
				elif(self._checkLine(line=line, prefix=self._config.getEndMultiComm())):
					result.append(line)
					break
				elif (isStarted or self._checkLine(line=line, prefix=self._config.getSingleComm())):
					result.append(line)
				else:
					break
		return result
	def _checkLicense(self, test: list[str]):
		license = self.getLicense()
		_test = ''.join(test)
		return license == _test
	def checkFile(self, pathToFile: str):
		"""Checks a file for a valid license."""
		with open(pathToFile, 'r', encoding="utf8") as file:
			test = []
			if (self._config.getCheckLines()):
				lines = []
				for i in range(self._config.getCheckLines()):
					lines.append(file.readline())
				test = self.findLicense(lines=lines)
			else:
				test = self.findLicense(lines=file.readlines())
			if test:
				result = self._checkLicense(test=test)
				if not result:
					self._reports.append(Report(pathToFile=pathToFile, error=Error(errorType=ErrorType.INVALID_LICENSE)))
			else:
				self._reports.append(Report(pathToFile=pathToFile, error=Error(errorType=ErrorType.NO_LICENSE)))
		return
class Walker(object):
	def __init__(self, config: Config) -> None:
		self._config = config
		self._checker = Checker(config=self._config)
	def getChecker(self):
		return self._checker
	def getConfig(self):
		return self._config
	def _getFiles(self) -> list[str]:
		result = []
		for address, dirs, files in os.walk(self._config.getDir()):
			for i in self._config.getIgnoreListDir():
				if(re.search(re.escape(os.path.normpath(i)), address)):
					break
			else:
				for i in files:
					for j in self._config.getIgnoreListFile():
						if (os.path.normpath(j) == os.path.join(address, i)):
							break
					else:
						filename, file_extension = os.path.splitext(i)
						for j in self._config.getFileExtensions():
							if (file_extension == j):
								result.append(os.path.join(address, i))
		return result
	def checkFiles(self) -> list[Report]:
		print('Getting files...')
		files = self._getFiles()
		for file in files:
			print(f'Checking {file}...')
			self._checker.checkFile(file)
		return self._checker.getReports()

class Fixer(object):
	def __init__(self, walker: Walker) -> None:
		self._walker = walker
		self._checker = self._walker.getChecker()
		self._config = self._walker.getConfig()
	def fix(self):
		for report in self._checker.getReports():
			if (report.getError().getErrorType() == ErrorType.NO_LICENSE):
				self._addLicense(report.getPathToFile())
			elif (report.getError().getErrorType() == ErrorType.INVALID_LICENSE):
				self._fixLicense(report.getPathToFile())
		return
	def _addLicense(self, pathToFile: str):
		buffer = []
		with open(pathToFile, 'r', encoding="utf8") as file:
			buffer = file.readlines()
		with open(pathToFile, 'w', encoding="utf8") as file:
			license = self._checker.getLicense()
			file.write(license)
			file.writelines(buffer)
		return
	def _fixLicense(self, pathToFile: str):
		buffer = []
		result = []
		with open(pathToFile, 'r', encoding="utf8") as file:
			buffer = file.readlines()
			oldLicense = self._checker.findLicense(buffer)
			for i in oldLicense:
				buffer.remove(i)
			license = self._checker.getLicense().splitlines(True)
			result = license + buffer
		with open(pathToFile, 'w', encoding="utf8") as file:
			file.writelines(result)
		return

config = Config(
	dir='sdkjs',
	singleComm='//',
	fileExtensions=['.js'],
	startMultiComm='/*',
	endMultiComm='*/',
	prefix='*',
	ignoreListDir=[
		'sdkjs/build/node_modules',
		'sdkjs/build/maps',
		'sdkjs/.github',
		'sdkjs/deploy',
		'sdkjs/develop',
		'sdkjs/vendor',
		'sdkjs/configs',
		'sdkjs/pdf/test/vendor'
	]
)

walker = Walker(config=config)
reports = walker.checkFiles()
if reports:
	print('\n'.join(map(lambda report: report.report(), reports)))
	choice = str(input(f'{len(reports)} invalid licenses were found, fix it automatically? [Y/N]')).lower()
	if choice == 'y':
		fixer = Fixer(walker=walker)
		print(f'Fixind all {len(reports)} files...')
		fixer.fix()
		print('Done.')
else:
	print('All licenses are ok')


os.system('pause')