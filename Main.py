import os
import sys
import glob

if(len(sys.argv) < 2):
    exit()

file = open('samples.xml', 'r+')
file.seek(0, os.SEEK_SET)
fileContent = file.read().split('"')

file.seek(0, os.SEEK_SET)
file.write(fileContent[0])
file.write('"')
file.write(sys.argv[1])
file.write('"')

for i in range(2, len(fileContent)):
    if (i % 2) != 0: 
        file.write('"')
    file.write(fileContent[i])
    if (i % 2) != 0:
        file.write('"')

file.close()

os.system('python ./wfc_2019f-master/wfc_run.py -s samples.xml')

list_of_files = glob.glob('./output/*.png')
latest_file = max(list_of_files, key=os.path.getctime)

rgb = ""

if(len(sys.argv) > 2):
    rgb = sys.argv[2]

os.system('python ./map_generation/src/Main.py ' + latest_file + " " + rgb)