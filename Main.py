import os
import sys
import glob

image = ""
rgb = ""
n = ""
periodic = ""
rotations = ""
xml = "samples.xml"
wfc = "true"

for i in range(1, len(sys.argv)):
    opt = sys.argv[i].split("=")

    if opt[0] == "image":
        image = opt[1] 
    elif opt[0] == "rgb":
        rgb = opt[1]
    elif opt[0] == "n":
        n = opt[1]
    elif opt[0] == "periodic":
        periodic = opt[1]
    elif opt[0] == "rotations":
        rotations = opt[1]
    elif opt[0] == "xml":
        xml = opt[1]
    elif opt[0] == "wfc":
        wfc = opt[1]
        
if wfc == "true":
    if image != "" or n != "" or periodic != "" or rotations != "":
        file = open(xml, 'r+')
        file.seek(0, os.SEEK_SET)
        fileContent = file.read().split('"')

        file.close()
        file = open(xml, 'w+')
        file.write(fileContent[0])

        for i in range(1, len(fileContent)):
            if (i % 2) != 0: 
                file.write('"')

            if i == 1 and image != "":
                file.write(image)
            elif i == 3 and n != "":
                file.write(n)
            elif i == 5 and periodic != "":
                file.write(periodic)
            elif i == 7 and rotations != "":
                file.write(rotations)
            else:
                file.write(fileContent[i])

            if (i % 2) != 0:
                file.write('"')

        file.close()

    os.system('python ./wfc_2019f-master/wfc_run.py -s ' + xml)

if wfc == "true" or image == "":
    list_of_files = glob.glob('./output/*.png')
    latest_file = max(list_of_files, key=os.path.getctime)
else:
    latest_file = "./output/" + image


os.system('python ./map_generation/src/Main.py ' + latest_file + " " + rgb)