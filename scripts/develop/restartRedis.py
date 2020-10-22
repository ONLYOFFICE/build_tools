import os
import sys
sys.path.append('../')

os.system('taskkill /IM redis-server.exe')
os.system('sc start Redis')
