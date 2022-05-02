import time

import noise
import grpc
import random

import minecraft_pb2_grpc
from minecraft_pb2 import *

channel = grpc.insecure_channel('localhost:5001')
client = minecraft_pb2_grpc.MinecraftServiceStub(channel)

"""
Simple genetic algorithm guessing a string.
"""
# Enter here the string to be searched
EXPECTED_HEIGHT = 8

# Enter here the chance for an individual to mutate (range 0-1)
CHANCE_TO_MUTATE = 0.1

# Enter here the percent of top-grated individuals to be retained for the next generation (range 0-1)
GRADED_RETAIN_PERCENT = 0.4

# Enter here the chance for a non top-grated individual to be retained for the next generation (range 0-1)
CHANCE_RETAIN_NONGRATED = 0.05

# Number of individual in the population
POPULATION_COUNT = 100

# Maximum number of generation before stopping the script
GENERATION_COUNT_MAX = 50

# ----- Do not touch anything after this line

# Number of top-grated individuals to be retained for the next generation
GRADED_INDIVIDUAL_RETAIN_COUNT = int(POPULATION_COUNT * GRADED_RETAIN_PERCENT)

# Maximum fitness value
MAXIMUM_FITNESS = 12

choice = lambda x: x[int(random.random() * len(x))]


# ----- Genetic Algorithm code
# Note: An individual is simply an array of LENGTH_OF_EXPECTED_STR characters.
# And a population is nothing more than an array of individuals.


def get_random_block():
    x = random.randrange(0, 50)
    z = random.randrange(0, 50)
    y = 1
    min_y = 1
    max_y = 11
    column = client.readCube(Cube(
        min=Point(x=x, y=min_y, z=z),
        max=Point(x=x, y=max_y, z=z)
    ))
    for block in column.blocks:
        if block.type == AIR:
            y = block.position.y
            break

    return Block(position=Point(x=x, y=y, z=z),
                 type=DIAMOND_BLOCK,
                 orientation=NORTH
                 )


def get_block(x, z):
    y = 1
    min_y = 1
    max_y = 11
    column = client.readCube(Cube(
        min=Point(x=x, y=min_y, z=z),
        max=Point(x=x, y=max_y, z=z)
    ))
    for block in column.blocks:
        if block.type == AIR:
            y = block.position.y
            break

    return Block(position=Point(x=x, y=y, z=z),
                 type=DIAMOND_BLOCK,
                 orientation=NORTH
                 )


def get_random_population():
    _blocks = []
    for individuals in range(POPULATION_COUNT):
        _blocks.append(get_random_block())
    client.spawnBlocks(Blocks(blocks=_blocks))
    return _blocks


def get_individual_fitness(individual):
    if individual >= EXPECTED_HEIGHT:
        return 1
    return 0


def average_population_grade(population):
    """ Return the average fitness of all individual in the population. """
    total = 0
    for individual in population:
        total += get_individual_fitness(individual.position.y)
    return total / POPULATION_COUNT


def grade_population(population):
    """ Grade the population. Return a list of tuple (individual, fitness) sorted from most graded to less graded. """
    graded_individual = []
    for individual in population:
        graded_individual.append((individual, get_individual_fitness(individual.position.y)))
    return sorted(graded_individual, key=lambda x: x[1], reverse=True)


def evolve_population(population):
    """ Make the given population evolving to his next generation. """

    # Get individual sorted by grade (top first), the average grade and the solution (if any)
    raw_graded_population = grade_population(population)
    average_grade = 0
    solution = []
    graded_population = []
    for individual, fitness in raw_graded_population:
        average_grade += fitness
        graded_population.append(individual)
        if fitness == MAXIMUM_FITNESS:
            solution.append(individual)
    average_grade /= POPULATION_COUNT

    # End the script when solution is found
    if solution:
        return population, average_grade, solution

        # Filter the top graded individuals
    parents = graded_population[:GRADED_INDIVIDUAL_RETAIN_COUNT]

    # Randomly add other individuals to promote genetic diversity

    for individual in graded_population[GRADED_INDIVIDUAL_RETAIN_COUNT:]:
        if random.random() < CHANCE_RETAIN_NONGRATED:
            parents.append(individual)

    # Mutate some individuals
    for individual in parents:
        if random.random() < CHANCE_TO_MUTATE:
            individual = get_random_block()

    # Crossover parents to create children
    parents_len = len(parents)
    desired_len = POPULATION_COUNT - parents_len
    children = []
    while len(children) < desired_len:
        father = choice(parents)
        mother = choice(parents)
        if True:  # father != mother:
            child = get_block(x=father.position.x, z=mother.position.z)
            children.append(child)

    # The next generation is ready
    parents.extend(children)
    _blocks = []
    for block in parents:
        _blocks.append(Block(position=(Point(x=block.position.x, y=block.position.y, z=block.position.z)), type=DIAMOND_BLOCK))
        client.spawnBlocks(Blocks(blocks=_blocks))


    return parents, average_grade, solution


def clear_population(population):
    _blocks = []
    for block in population:
        _blocks.append(Block(position=(Point(x=block.position.x, y=block.position.y, z=block.position.z)), type=AIR))
        client.spawnBlocks(Blocks(blocks=_blocks))


# ----- Runtime code


def start_generation():
    """ Main function. """

    # Create a population and compute starting grade
    population = get_random_population()
    average_grade = average_population_grade(population)
    print('Starting grade: %.2f' % average_grade, '/ %d' % MAXIMUM_FITNESS)
    time.sleep(1)
    # Make the population evolve
    i = 0
    solution = None
    log_avg = []
    while not solution and i < GENERATION_COUNT_MAX:
        clear_population(population)
        time.sleep(1)
        population, average_grade, solution = evolve_population(population)
        i += 1
        if i & 255 == 255:
            print('Current grade: %.2f' % average_grade, '/ %d' % MAXIMUM_FITNESS, '(%d generation)' % i)
        if i & 31 == 31:
            log_avg.append(average_grade)
        i += 1

        import pygal

        line_chart = pygal.Line(show_dots=False, show_legend=False)
        line_chart.title = 'Fitness evolution'
        line_chart.x_title = 'Generations'
        line_chart.y_title = 'Fitness'
        line_chart.add('Fitness', log_avg)
        line_chart.render_to_file('bar_chart.svg')

        # Print the final stats
        average_grade = average_population_grade(population)
        print('Final grade: %.2f' % average_grade, '/ %d' % MAXIMUM_FITNESS)

        # Print the solution
        if solution:
            print('Solution found (%d times) after %d generations.' % (len(solution), i))
        else:
            print('No solution found after %d generations.' % i)
            print('- Last population was:')
            for number, individual in enumerate(population):
                print(number, '->', individual.position.x + individual.position.y, individual.position.z)
        print("waiting")
        time.sleep(1)

