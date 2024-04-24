import os
import re
import enum
import json
import codecs

CONFIG_PATH = 'config.json'

class ErrorType(enum.Enum):
	INVALID_LICENSE = 1
	NO_LICENSE = 2
	OUTDATED = 3
	LEN_MISMATCH = 4

FIX_TYPES = {
	'OUTDATED': ErrorType.OUTDATED,
	'NO_LICENSE': ErrorType.NO_LICENSE,
	'INVALID_LICENSE': ErrorType.INVALID_LICENSE,
	'LEN_MISMATCH': ErrorType.LEN_MISMATCH
}

class Config(object):
	"""
	License checker configuration.
	Attributes:
		dir: Directory to check.
		fileExtensions: file extensions to check.
		ignoreListDir: Ignored folder paths.
		ignoreListDirName: Ignored folder names.
		ignoreListFile: Ignored file paths.
		allowListFile: allow file paths.
	"""
	def __init__(self,
		dir: str,
		fileExtensions: list[str],
		licensePath: str = 'header.license',
		allowListFile: list[str] = [],
		ignoreListDir: list[str] = [],
		ignoreListDirName: list[str] = [],
		ignoreListFile: list[str] = []) -> None:

		self._dir = dir
		self._fileExtensions = fileExtensions
		self._allowListFile = allowListFile
		self._ignoreListDir = ignoreListDir
		self._ignoreListDirName = ignoreListDirName
		self._ignoreListFile = ignoreListFile
		"""Read license template."""
		with open(licensePath, 'r', encoding="utf8") as file:
			lines = file.readlines()
			if not lines:
				raise Exception(f'Error getting license template. Cannot read {licensePath} file. Is not it empty?')
			non_empty_lines = [s for s in lines if not s.isspace()]
			self._startMultiComm = non_empty_lines[0]
			self._endMultiComm = non_empty_lines[-1]
			self._license_lines = lines

	def getDir(self) -> str:
		return self._dir
	def getFileExtensions(self) -> list[str]:
		return self._fileExtensions
	def getStartMultiComm(self) -> str:
		return self._startMultiComm
	def getEndMultiComm(self) -> str:
		return self._endMultiComm
	def getLicense(self) -> list[str]:
		return self._license_lines
	def getAllowListFile(self) -> list[str]:
		return self._allowListFile
	def getIgnoreListDir(self) -> list[str]:
		return self._ignoreListDir
	def getIgnoreListDirName(self) -> list[str]:
		return self._ignoreListDirName
	def getIgnoreListFile(self) -> list[str]:
		return self._ignoreListFile

with open(CONFIG_PATH, 'r') as j:
	_json: dict = json.load(j)
	BASE_PATH: str = _json.get('basePath') or '../../../'
	REPORT_FOLDER: str = _json.get('reportFolder') or 'build_tools/scripts/license_checker/reports'
	if (_json.get('fix')):
		try:
			FIX: list[ErrorType] = list(map(lambda x: FIX_TYPES[x], _json.get('fix')))
		except KeyError:
			raise Exception(f'KeyError. "fix" cannot process value. It must be an array of strings. Check {CONFIG_PATH}. Possible array values: "OUTDATED", "NO_LICENSE", "INVALID_LICENSE", "LEN_MISMATCH"')
	else:
		FIX = False
	PRINT_CHECKING: bool = _json.get('printChecking')
	PRINT_REPORTS: bool = _json.get('printReports')
	CONFIGS: list[Config] = []
	for i in _json.get('configs'):
		CONFIGS.append(Config(**i))

os.chdir(BASE_PATH)

class Error(object):
	def __init__(self, errorType: ErrorType) -> None:
		self._errorType = errorType
		self._errorMessages = {
			ErrorType.INVALID_LICENSE: 'Detected license is invalid',
			ErrorType.NO_LICENSE: 'The license was not found',
			ErrorType.OUTDATED: 'Detected license is outdated',
			ErrorType.LEN_MISMATCH: 'Detected license length does not match pattern'
		}
	def getErrorType(self) -> ErrorType:
		return self._errorType
	def getErrorMessage(self) -> str:
		return self._errorMessages.get(self._errorType)
		
class Report(object):
	def __init__(self, pathToFile: str, error: Error, message:str = '') -> None:
		self._pathToFile = pathToFile
		self._error = error
		self._message = message
	def getPathToFile(self) -> str:
		return self._pathToFile
	def getError(self) -> Error:
		return self._error
	def getMessage(self) -> str:
		return self._message
	def report(self) -> str:
		return f'{self.getPathToFile()}: {self.getError().getErrorMessage()}. {self.getMessage()}.'

class Checker(object):
	def __init__(self, config: Config) -> None:
		self._config = config
		self._reports: list[Report] = []
	def getReports(self):
		return self._reports
	def _checkLine(self, line: str, prefix: str) -> bool:
		"""Checks if a line has a prefix."""
		"""Trim to catch invalid license without leading spaces"""
		prefix = prefix.lstrip()
		if (re.search(re.escape(prefix), line)):
			return True
		else:
			return False
	def findLicense(self, lines: list[str]) -> list[str]:
		"""Looks for consecutive comments in a list of strings."""
		result = []
		isStarted = False
		for line in lines:
			if line == '\n': continue
			if (self._checkLine(line=line, prefix=self._config.getStartMultiComm())):
				result.append(line)
				isStarted = True
			elif(self._checkLine(line=line, prefix=self._config.getEndMultiComm())):
				result.append(line)
				break
			elif (isStarted):
				result.append(line)
			else:
				break
		return result
	def _checkLicense(self, test: list[str], pathToFile: str) -> Report:
		license = self._config.getLicense()
		if len(license) != len(test):
			return Report(pathToFile=pathToFile,
				error=Error(errorType=ErrorType.LEN_MISMATCH),
				message=f'Found {len(test)} lines, expected {len(license)}')
		invalidLinesCount = 0
		lastWrongLine = 0
		for i in range(len(license)):
			if (license[i] != test[i]):
				invalidLinesCount += 1
				lastWrongLine = i
		if (invalidLinesCount == 1):
			r = r'\d\d\d\d'
			testDate = re.findall(r, test[lastWrongLine])
			licenseDate = re.findall(r, license[lastWrongLine])

			if not (testDate and licenseDate):
				return Report(pathToFile=pathToFile,
				error=Error(errorType=ErrorType.INVALID_LICENSE),
				message=f'Something wrong...')

			testLastYear = int(testDate[-1])
			licenseLastYear = int(licenseDate[-1])
			if (testLastYear < licenseLastYear):
				return Report(pathToFile=pathToFile,
					error=Error(errorType=ErrorType.OUTDATED),
					message=f'Found date {testLastYear}, expected {licenseLastYear}')
			else:
				return Report(pathToFile=pathToFile,
					error=Error(errorType=ErrorType.INVALID_LICENSE),
					message=f"Found something similar to the date: {testLastYear}, but it's not correct. Expected: {licenseLastYear}")
		elif (invalidLinesCount > 0):
			return Report(pathToFile=pathToFile,
				error=Error(errorType=ErrorType.INVALID_LICENSE),
				message=f'Found {invalidLinesCount} wrong lines out of {len(license)}')
	def checkFile(self, pathToFile: str) -> None:
		"""Checks a file for a valid license."""
		with open(pathToFile, 'r', encoding="utf-8-sig") as file:
			test = self.findLicense(lines=file.readlines())
			if test:
				result = self._checkLicense(test=test, pathToFile=pathToFile)
				if result:
					self._reports.append(result)
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
			for i in files:
				if (os.path.join(address, i) in list(map(lambda x: os.path.normpath(x), self._config.getAllowListFile()))):
					filename, file_extension = os.path.splitext(i)
					if file_extension in self._config.getFileExtensions():
						result.append(os.path.join(address, i))
			else:
				for i in self._config.getIgnoreListDirName():
					if(re.search(re.escape(i), address)):
						break
				else:
					for i in self._config.getIgnoreListDir():
						if(re.search(re.escape(os.path.normpath(i)), address)):
							break
					else:
						for i in files:
							if not (os.path.join(address, i) in list(map(lambda x: os.path.normpath(x), self._config.getIgnoreListFile()))):
								filename, file_extension = os.path.splitext(i)
								if file_extension in self._config.getFileExtensions():
									result.append(os.path.join(address, i))
		return result
	def checkFiles(self) -> list[Report]:
		files = self._getFiles()
		for file in files:
			if (PRINT_CHECKING):
				print(f'Checking {file}...')
			# self._checker.checkFile(file)
			try:
				self._checker.checkFile(file)
			except Exception as e:
				print(file)	
				print(e)			
		return self._checker.getReports()

class Fixer(object):
	def __init__(self, walker: Walker) -> int:
		self._walker = walker
		self._checker = self._walker.getChecker()
		self._config = self._walker.getConfig()
	def fix(self):
		count = 0
		for report in self._checker.getReports():
			if ((not FIX and report.getError().getErrorType() == ErrorType.NO_LICENSE) or (report.getError().getErrorType() == ErrorType.NO_LICENSE and report.getError().getErrorType() in FIX)):
				self._addLicense(report.getPathToFile())
				count += 1
			elif ((not FIX and report.getError().getErrorType() != ErrorType.NO_LICENSE) or (report.getError().getErrorType() != ErrorType.NO_LICENSE and report.getError().getErrorType() in FIX)):
				self._fixLicense(report.getPathToFile())
				count += 1
		return count
	def _addLicense(self, pathToFile: str):
		buffer = []
		with open(pathToFile, 'r', encoding="utf8") as file:
			buffer = file.readlines()
		with open(pathToFile, 'w', encoding="utf8") as file:
			license = self._config.getLicense()
			file.writelines(license)
			file.write('\n')
			file.writelines(buffer)
		return
	def _fixLicense(self, pathToFile: str):
		buffer = []
		writeEncoding = "utf8"
		with open(pathToFile, 'r', encoding="utf8") as file:
			buffer = file.readlines()
			if buffer and buffer[0].startswith(codecs.decode(codecs.BOM_UTF8)):
				writeEncoding = "utf-8-sig"
			oldLicense = self._checker.findLicense(buffer)
			for i in oldLicense:
				buffer.remove(i)
		with open(pathToFile, 'w', encoding=writeEncoding) as file:
			license = self._config.getLicense()
			file.writelines(license)
			file.writelines(buffer)
		return


walkers: list[Walker] = []
reports: list[Report] = []

def fix(walkers):
	count = 0
	if FIX:
		print(f'Fixing selected files...')
	else:
		print(f'Fixing all {len(reports)} files...')
	for walker in walkers:
		fixer = Fixer(walker=walker)
		count += fixer.fix()
	print(f'Fixed {count} files.')

def writeReports(reports: list[Report]) -> None:
	files: dict[str, list[Report]] = dict()
	for i in ErrorType:
		files[i.name] = []
	for i in reports:
		files[i.getError().getErrorType().name].append(i)
	for i in ErrorType:
		with open(f'{REPORT_FOLDER}/{i.name}.txt', 'w', encoding="utf8") as f:
			f.writelines(map(lambda x: "".join([x.report(), '\n']), files.get(i.name)))

for config in CONFIGS:
	walkers.append(Walker(config=config))

print('Checking files...')

for walker in walkers:
	reports = reports + walker.checkFiles()

if reports:
	if not os.path.exists(REPORT_FOLDER):
		os.mkdir(REPORT_FOLDER)
	if PRINT_REPORTS:
		print('\n'.join(map(lambda report: report.report(), reports)))
	print(f'{len(reports)} invalid licenses were found.')
	print(f'Saving reports in {REPORT_FOLDER}')
	writeReports(reports=reports)
	if FIX:
		fix(walkers=walkers)
	# else:
		# choice = str(input(f'Fix it automatically? [Y/N] ')).lower()
		# if choice == 'y':
			# fix(walkers=walkers)
else:
	print('All licenses are ok.')

# os.system('pause')

