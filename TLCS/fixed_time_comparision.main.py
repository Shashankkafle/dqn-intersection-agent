from __future__ import absolute_import
from __future__ import print_function

import os
from shutil import copyfile

from fixed_time_sim import Simulation
from generator import TrafficGenerator
from model import TestModel
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path


if __name__ == "__main__":

    config = import_test_configuration(config_file='testing_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    model_path, plot_path = set_test_path(config['models_path_name'], config['model_to_test'])

    Model = TestModel(
        input_dim=config['num_states'],
        model_path=model_path
    )

    TrafficGen = TrafficGenerator(
        config['max_steps'], 
        config['n_cars_generated']
    )

    Model_Visualization = Visualization(
        "C:/Users/GIS2025/Q-learning/Deep-QLearning-Agent-for-Traffic-Signal-Control/TLCS/model_comparision", 
        dpi=96
    )
    Cyclic_Visualization = Visualization(
        "C:/Users/GIS2025/Q-learning/Deep-QLearning-Agent-for-Traffic-Signal-Control/TLCS/cyclic_comparision", 
        dpi=96
    )
        
    Model_Simulation = Simulation(
        Model,
        TrafficGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['num_states'],
        config['num_actions'],
        False
    )
    Cyclic_Simulation = Simulation(
        Model,
        TrafficGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['num_states'],
        config['num_actions'],
        True
    )

    print('\n----- Test episode')
    simulation_time = Model_Simulation.run(config['episode_seed'])  # run the simulation
    simulation_time = Cyclic_Simulation.run(config['episode_seed'])  # run the simulation
    print('Simulation time:', simulation_time, 's')

    print("----- Testing info saved at:", plot_path)

    copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

    Model_Visualization.save_data_and_plot(data=Model_Simulation.reward_episode, filename='reward', xlabel='Action step', ylabel='Reward')
    Model_Visualization.save_data_and_plot(data=Model_Simulation.queue_length_episode, filename='queue', xlabel='Step', ylabel='Queue lenght (vehicles)')
    Model_Visualization.save_data_and_plot(data=Model_Simulation.avg_wait_episode, filename='average_wait', xlabel='Step', ylabel='Average wait (vehicles)')
    Cyclic_Visualization.save_data_and_plot(data=Cyclic_Simulation.reward_episode, filename='reward', xlabel='Action step', ylabel='Reward')
    Cyclic_Visualization.save_data_and_plot(data=Cyclic_Simulation.queue_length_episode, filename='queue', xlabel='Step', ylabel='Queue lenght (vehicles)')
    Cyclic_Visualization.save_data_and_plot(data=Cyclic_Simulation.avg_wait_episode, filename='average_wait', xlabel='Step', ylabel='Average Wait (vehicles)')
