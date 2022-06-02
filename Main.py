import os
import sys
import glob

if(len(sys.argv) < 2):
    exit()

os.system('python ./wfc_2019f-master/wfc_run.py -s ' + sys.argv[1])

list_of_files = glob.glob('./output/*.png')
latest_file = max(list_of_files, key=os.path.getctime)

rgb = ""

if(len(sys.argv) > 2):
    rgb = sys.argv[2]

os.system('python ./map_generation/src/Main.py ' + latest_file + " " + rgb)