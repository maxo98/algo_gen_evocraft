import PIL
import grpc
from PIL.Image import Image
from osgeo import gdal
from osgeo import gdal_array
import numpy as np
import matplotlib.pyplot as plt
import sys

import minecraft_pb2_grpc
from minecraft_pb2 import *

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)


image_block = []


def init_img():
    image = PIL.Image.open(filename)
    image = image.convert('RGB')
    pix = image.load()
    for x in range(image.size[0]):
        image_block.append([])
        for y in range(image.size[1]):
            if image_type == 'rgb':
                image_block[x].append(color_to_block(pix[x, y]))
            else:
                image_block[x].append(color_to_height(pix[x, y]))


def color_to_block(color):
    if color[0] < 128:
        if color[1] < 128:
            if color[2] < 128:
                return OBSIDIAN
            else:
                return LAPIS_BLOCK
        else:
            if color[2] < 128:
                return EMERALD_BLOCK
            else:
                return PACKED_ICE
    else:
        if color[1] < 128:
            if color[2] < 128:
                return REDSTONE_BLOCK
            else:
                return GOLD_BLOCK
        else:
            if color[2] < 128:
                return PINK_GLAZED_TERRACOTTA
            else:
                return WOOL


def color_to_height(color):
    return color[0]/50


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
    for x in range(len(image_block)):
        for y in range(len(image_block[0])):
            _blocks.append(Block(position=Point(x=x, y=0, z=y), type=image_block[x][y]))
    client.spawnBlocks(Blocks(blocks=_blocks))


def spawn_height_map():
    _blocks = []
    for x in range(len(image_block)):
        for y in range(len(image_block[0])):
            _blocks.append(Block(position=Point(x=x, y=int(image_block[x][y]), z=y), type=STONEBRICK))
    client.spawnBlocks(Blocks(blocks=_blocks))


if(len(sys.argv) < 2):
    exit()

clear_map()
filename = sys.argv[1]

image_type = ""

if(len(sys.argv) > 2):
    image_type = sys.argv[2]

init_img()
if image_type == 'rgb':
    spawn_map()
else:
    spawn_height_map()


print("done")