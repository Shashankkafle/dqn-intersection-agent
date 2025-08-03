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
    model_path, plot_path, comaprision_path = set_test_path(config['models_path_name'], config['model_to_test'])

    Model = TestModel(
        input_dim=config['num_states'],
        model_path=model_path
    )

    TrafficGen = TrafficGenerator(
        config['max_steps'], 
        config['n_cars_generated']
    )

    visualization = Visualization(
       comaprision_path, 
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

    visualization.save_data_and_plot(data=Model_Simulation.reward_episode, filename='model_reward', xlabel='Action step', ylabel='Reward')
    visualization.save_data_and_plot(data=Model_Simulation.queue_length_episode, filename='model_queue', xlabel='Step', ylabel='Queue lenght (vehicles)')
    visualization.save_data_and_plot(data=Model_Simulation.avg_wait_episode, filename='model_average_wait', xlabel='Step', ylabel='Average wait (vehicles)')
    visualization.save_data_and_plot(data=Cyclic_Simulation.reward_episode, filename='fixed_time_reward', xlabel='Action step', ylabel='Reward')
    visualization.save_data_and_plot(data=Cyclic_Simulation.queue_length_episode, filename='fixed_time_queue', xlabel='Step', ylabel='Queue lenght (vehicles)')
    visualization.save_data_and_plot(data=Cyclic_Simulation.avg_wait_episode, filename='fixed_time_average_wait', xlabel='Step', ylabel='Average Wait (vehicles)')
