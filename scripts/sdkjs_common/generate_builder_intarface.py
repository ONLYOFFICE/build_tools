#!/usr/bin/env python
import os
def readFile(path):
  with open(path, "r", encoding="utf-8") as file:
    filedata = file.read()
  return filedata

def writeFile(path, content):
  with open(path, "w", encoding="utf-8") as file:
    file.write(content)
  return

arrAllCorrectedRecords = []

def correctRecord(recordData):
  global arrAllCorrectedRecords
  rec = recordData
  rec = rec.replace("\t", "")
  rec = rec.replace('\n    ', '\n')
  indexEndDecoration = rec.find("*/")
  decoration = "/**" + rec[0:indexEndDecoration + 2]
  decoration = decoration.replace("Api\n", "ApiInterface\n")
  decoration = decoration.replace("Api ", "ApiInterface ")
  decoration = decoration.replace("{Api}", "{ApiInterface}")
  if -1 != decoration.find("@name ApiInterface"):
    arrAllCorrectedRecords.append(decoration + "\nvar ApiInterface = function() {};\n")
  code = rec[indexEndDecoration + 2:]
  code = code.strip("\t\n\r ")
  lines = code.split("\n")
  codeCorrect = ""
  sFuncName = ""
  is_found_function = False
  for line in lines:
    line = line.strip("\t\n\r ")
    line = line.replace("{", "")
    line = line.replace("}", "")
    if not is_found_function and 0 == line.find("function "):
      codeCorrect += (line + "{}\n")
      is_found_function = True
      sFuncName = get_func_name(line)
    if not is_found_function and -1 != line.find(".prototype."):
      codeCorrect += (line + "{}\n")
      is_found_function = True
      sFuncName = get_func_name(line)
    if ('' != sFuncName):
      del_from_records(sFuncName)
    if -1 != line.find(".prototype="):
      codeCorrect += (line + "\n")
    if -1 != line.find(".prototype.constructor"):
      codeCorrect += (line + "\n")
  codeCorrect = codeCorrect.replace("Api.prototype", "ApiInterface.prototype")

  arrAllCorrectedRecords.append(decoration + "\n" + codeCorrect)

def convert_to_interface(sPath, sEditorType):
  global arrAllCorrectedRecords
  file_content = readFile(sPath)
  arrRecords = file_content.split("/**")
  arrRecords = arrRecords[1:-1]
  correctContent = ""
  for record in arrRecords:
    correctRecord(record)
  correctContent += ''.join(arrAllCorrectedRecords)
  correctContent += "\nvar Api = new ApiInterface();"
  if False == os.path.isdir('../../sdkjs/deploy/apiInterface'):
    os.mkdir('../../sdkjs/deploy/apiInterface')
  if False == os.path.isdir('../../sdkjs/deploy/apiInterface/' + sEditorType):
    os.mkdir('../../sdkjs/deploy/apiInterface/' + sEditorType)
  writeFile("../../sdkjs/deploy/apiInterface/" + sEditorType + "/apiInterface.js", correctContent)

def get_func_name(sLine):
  if -1 != sLine.find('.prototype.'):
    return sLine.split('.prototype.')[1].split('=')[0].replace(' ', '')
  if -1 != sLine.find('function '):
    return sLine.split('function ')[1].split('(')[0]
  return ''

def del_from_records(sFuncOrClassName):
  global arrAllCorrectedRecords
  for nRecord in range(len(arrAllCorrectedRecords)):
    if -1 != arrAllCorrectedRecords[nRecord].find(sFuncOrClassName):
      arrAllCorrectedRecords[nRecord] = ''

convert_to_interface("../../sdkjs/word/apiBuilder.js", "word")
convert_to_interface("../../sdkjs/slide/apiBuilder.js", "slide")
convert_to_interface("../../sdkjs/cell/apiBuilder.js", "cell")

