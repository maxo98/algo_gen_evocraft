import grpc
from osgeo import gdal
from osgeo import gdal_array
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt

import minecraft_pb2_grpc
from minecraft_pb2 import *

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

filename = "ldem_64.tif"
gdal_data = gdal.Open(filename, gdal.GA_ReadOnly)

gdal_band = gdal_data.GetRasterBand(1)
nodataval = gdal_band.GetNoDataValue()

# Projection
print(gdal_data.GetProjection())

# Dimensions
print(gdal_data.RasterXSize)
print(gdal_data.RasterYSize)

# Number of bands
print(gdal_data.RasterCount)

# Metadata for the raster dataset
print(gdal_data.GetMetadata())

print("done 0")

# convert to a numpy array
#data_array = gdal_data.ReadAsArray().astype(float)

# replace missing values if necessary
#data_array = np.ma.masked_equal(data_array, nodataval)

# Compute statistics if needed
if gdal_band.GetMinimum() is None or gdal_band.GetMaximum() is None:
    gdal_band.ComputeStatistics(0)
    print("Statistics computed.")

# Fetch metadata for the band
gdal_band.GetMetadata()

# Print only selected metadata:
print ("[ NO DATA VALUE ] = ", gdal_band.GetNoDataValue()) # none
minimum =  gdal_band.GetMinimum()
print("[ MIN ] = ", minimum)
print ("[ MAX ] = ", gdal_band.GetMaximum())

print("done 1")

# Allocate our array using the first band's datatype
image_datatype = gdal_data.GetRasterBand(1).DataType

image = np.zeros((gdal_data.RasterYSize, gdal_data.RasterXSize, gdal_data.RasterCount),
                 dtype=gdal_array.GDALTypeCodeToNumericTypeCode(image_datatype))

# Loop over all bands in dataset
for b in range(gdal_data.RasterCount):
    # Remember, GDAL index is on 1, but Python is on 0 -- so we add 1 for our GDAL calls
    band = gdal_data.GetRasterBand(b + 1)
    
    # Read in the band's data into the third dimension of our array
    image[:, :, b] = band.ReadAsArray()

plt.imshow(image[:, :, gdal_data.RasterCount-1])
plt.colorbar()
#plt.show()

print("done 2")

def clear_map():
    client.fillCube(FillCubeRequest(
        cube=Cube(
            min=Point(x=0, y=0, z=0),
            max=Point(x=500, y=128, z=500)
        ),
        type=AIR
    ))

def spawn_map():
    _blocks = []
    print(len(image))
    print(len(image[0]))
    for x in range(100):
        for y in range(100):
            _blocks.append(Block(position=Point(x=x, y=int(image[x*10][y*10] - minimum) , z=y), type=STONEBRICK))
            _blocks.append(Block(position=Point(x=x, y=int(image[x*10][y*10] - minimum) -1 , z=y), type=STONEBRICK))

    client.spawnBlocks(Blocks(blocks=_blocks))
    _blocks.clear()
    for x in range(100, 200):
        for y in range(100):
            _blocks.append(Block(position=Point(x=x, y=int(image[x*10][y*10] - minimum) , z=y), type=DIAMOND_BLOCK))
            _blocks.append(Block(position=Point(x=x, y=int(image[x*10][y*10] - minimum) -1 , z=y), type=DIAMOND_BLOCK))

    client.spawnBlocks(Blocks(blocks=_blocks))
    _blocks.clear()
    for x in range(100):
        for y in range(100,200):
            _blocks.append(Block(position=Point(x=x, y=int(image[x * 10][y * 10] - minimum), z=y), type=DIAMOND_BLOCK))
            _blocks.append(
                Block(position=Point(x=x, y=int(image[x * 10][y * 10] - minimum) - 1, z=y), type=DIAMOND_BLOCK))

    client.spawnBlocks(Blocks(blocks=_blocks))
    _blocks.clear()
    for x in range(100, 200):
        for y in range(100, 200):
            _blocks.append(Block(position=Point(x=x, y=int(image[x * 10][y * 10] - minimum), z=y), type=STONEBRICK))
            _blocks.append(
                Block(position=Point(x=x, y=int(image[x * 10][y * 10] - minimum) - 1, z=y), type=STONEBRICK))

    client.spawnBlocks(Blocks(blocks=_blocks))

clear_map()
spawn_map()
print("done")
#To free the data
#gdal_data = None
#gdal_band = None