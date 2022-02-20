import sys
sys.path.append('../../../scripts')
import base
import os

def make(build_js = True):

  old_cur_dir = os.getcwd()
  #fetch libhunspell
  print("[fetch & build]: hunspell")
  core_common_dir = base.get_script_dir() + "/../../core/Common"

  os.chdir(core_common_dir + "/3dParty/hunspell")
  base.cmd("python", ["./before.py"])

  if (build_js):
    os.chdir(core_common_dir + "/js")
    base.cmd("python", ["./make.py", core_common_dir + "/3dParty/hunspell/hunspell.json"])

  os.chdir(old_cur_dir)

if __name__ == '__main__':
  # manual compile
  make(True)
