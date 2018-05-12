"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
# import visualize
from neat.six_util import iteritems, itervalues

import random
from box_socket import socket_open , socket_close
from box_pi import Pigpio
import time

# 2-input XOR inputs and expected outputs.
xor_inputs = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (1.0, 1.0)]
xor_outputs = [   (0.0,),     (1.0,),     (1.0,),     (0.0,)]

def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = 4.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        for xi, xo in zip(xor_inputs, xor_outputs):
            output = net.activate(xi)
            genome.fitness -= (output[0] - xo[0]) ** 2

def eval_box(genomes,config,pi_gpio):

    servo_1 , servo_2 = pi_gpio.get_servo()
    decoder_1 = 0
    decoder_2 = 0
    input_data = [servo_1,servo_2]

    print("Servo 1 : {0} , Servo 2 : {1}".format(servo_1,servo_2))
    # print("Decoder 1 : {0} , Decoder 2 : {1}".format(decoder_1,decoder_2))

    for genome_id, genome in genomes:
        genome.fitness = 50
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = net.activate(input_data)
        # print("Output : {0}".format(output))
        if random.randint(0,100) > 90:
            pigpio.decoder_reset()
            if output[0] == 0 and output[1] == 0:
                pigpio.set_servo(random.uniform(0, 1),random.uniform(0, 1))
                # print ("set_servo %f , %f" , (random.uniform(0, 1),random.uniform(0, 1)))
            else:
                # print (" * set_servo %f , %f" , (output[0],output[1]))
                pigpio.set_servo(output[0],output[1])

        decoder_1 , decoder_2 = pi_gpio.get_decoder()
        print("Decoder 1 : {0} , Decoder 2 : {1}".format(decoder_1,decoder_2))

        result = (decoder_1+decoder_2)/2
        genome.fitness -= result

        # print("genome_fitness : {0}".format(genome.fitness))

def run(config_file , clientSocket , pigpio):

    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_box,eval_genomes, 300 , clientSocket , pigpio)

    # Display the winning genome.
    # for g in itervalues(p.population):
    #     print('\nGemome:\n{!s}'.format(g))

    # print('\nSpecies:\n{!s}'.format(p.species))

    # species_to_json(p.species);

    # print('\nBest genome:\n{!s}'.format(winner))

    # Show output of the most fit genome against training data.
    # print('\nOutput:')
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    for xi, xo in zip(xor_inputs, xor_outputs):
        output = winner_net.activate(xi)
        # print("input {!r}, expected output {!r}, got {!r}".format(xi, xo, output))

    # node_names = {-1:'A', -2: 'B', 0:'A XOR B'}
    # visualize.draw_net(config, winner, True, node_names=node_names)
    # visualize.plot_stats(stats, ylog=False, view=True)
    # visualize.plot_species(stats, view=True)

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    #p.run(eval_genomes, 10)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.

    # HOST = ''
    # PORT = 12345
    clientSocket = None
    # clientSocket = socket_open('',PORT)
    pigpio = Pigpio()
    # pigpio = None
    
    time.sleep(10)

    try:
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward')
        run(config_path , clientSocket , pigpio)
    except KeyboardInterrupt:
        # socket_close(clientSocket)
        # pigpio.close()
        print("bye~~")
