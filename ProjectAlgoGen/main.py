import time

import noise
import grpc
import random

import minecraft_pb2_grpc
from minecraft_pb2 import *
from algo_gen import *



def clear_map():
    client.fillCube(FillCubeRequest(
        cube=Cube(
            min=Point(x=0, y=4, z=0),
            max=Point(x=60, y=128, z=60)
        ),
        type=AIR
    ))


def spawn_map():
    x_seed = random.randint(0, 3000)
    y_seed = random.randint(0, 3000)

    map_size = (50, 50)

    _blocks = []
    for i in range(map_size[0]):
        for j in range(map_size[1]):
            nb_loop = int((noise.snoise2(i * 0.005 + x_seed, j * 0.005 + y_seed, 5, 6) + 1) * 5) + 4
            for cpt in range(nb_loop):
                _blocks.append(Block(position=Point(x=i, y=cpt, z=j), type=STONEBRICK))

    client.spawnBlocks(Blocks(blocks=_blocks))


def spawn_random_blocks():
    entities = []

    nb_entities = 50

    for entity in range(nb_entities):
        '''entities.append(Block(position=
                              Point(x=random.randrange(0, 50), y=20, z=random.randrange(0, 50)),
                              type=DIAMOND_BLOCK,
                              orientation=NORTH)
                        )'''
        entities.append(get_block())

    client.spawnBlocks(Blocks(blocks=entities))

clear_map()
time.sleep(1)
spawn_map()
start_generation()
#spawn_random_blocks()
