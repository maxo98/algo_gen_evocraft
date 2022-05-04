from osgeo import gdal
from osgeo import gdal_array
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt

filename = "ldac_50n_3000m.jp2"
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
print ("[ MIN ] = ", gdal_band.GetMinimum())
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
plt.show()

print("done 2")

#To free the data
#gdal_data = None
#gdal_band = None