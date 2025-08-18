from __future__ import absolute_import
from __future__ import print_function

import os
from shutil import copyfile

from fixed_time_sim import Simulation
from universal_generator import UniversalTrafficGenerator
from model import TestModel
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path
from fixed_duration_calculation import get_durations 


if __name__ == "__main__":

    config = import_test_configuration(config_file='testing_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    model_path, plot_path, comaprision_path = set_test_path(config['models_path_name'], config['model_to_test'])
    OUTPUT_TRIPS_FILE = os.getenv("OUTPUT_TRIPS_FILE")
    NET_FILE = os.getenv("NET_FILE")

    Model = TestModel(
        input_dim=config['num_states'],
        model_path=model_path
    )

    TrafficGen = UniversalTrafficGenerator(
        NET_FILE,
        OUTPUT_TRIPS_FILE,
        sim_end=config['max_steps'],
        vehicle_count= config['n_cars_generated'] 
    )
    route_weights = TrafficGen.generate_routefile(seed=0)

    visualization = Visualization(
       comaprision_path, 
        dpi=96
    )
    
    fixed_durations, lane_group_counts = get_durations(OUTPUT_TRIPS_FILE, config['max_steps'])

    Model_Simulation = Simulation(
        Model,
        TrafficGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['clearence_interval'],
        config['num_states'],
        config['num_actions'],
        False,
    )
    Cyclic_Simulation = Simulation(
        Model,
        TrafficGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['clearence_interval'],
        config['num_states'],
        config['num_actions'],
        True,
        durations=fixed_durations,
        
    )

    print('\n----- Test episode')
    simulation_time = Model_Simulation.run(config['episode_seed'])  # run the simulation
    simulation_time = Cyclic_Simulation.run(config['episode_seed'])  # run the simulation
    print('Simulation time:', simulation_time, 's')

    print("----- Testing info saved at:", plot_path)

    copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

    visualization.save_data_and_plot(data=Model_Simulation.reward_episode, filename='model_reward', xlabel='Action step', ylabel='Reward')
    visualization.save_data_and_plot(data=Model_Simulation.queue_length_episode, filename='model_queue', xlabel='Step', ylabel='Queue length (vehicles)')
    visualization.save_data_and_plot(data=Model_Simulation.avg_wait_episode, filename='model_average_wait', xlabel='Step', ylabel='Average wait (vehicles)')
    visualization.save_data_and_plot(data=Cyclic_Simulation.reward_episode, filename='fixed_time_reward', xlabel='Action step', ylabel='Reward')
    visualization.save_data_and_plot(data=Cyclic_Simulation.queue_length_episode, filename='fixed_time_queue', xlabel='Step', ylabel='Queue length (vehicles)')
    visualization.save_data_and_plot(data=Cyclic_Simulation.avg_wait_episode, filename='fixed_time_average_wait', xlabel='Step', ylabel='Average Wait (vehicles)')
    visualization.save_data(
        data=fixed_durations,
        filename='webster_fixed_timings'
    )
    visualization.save_data(
        data=lane_group_counts,
        filename='vehicles_per_lane_group'
    )
    visualization.save_data(
        data=route_weights,
        filename='route_weights'
    )
    visualization.overlayed_plot(
        fixed_time_data=Cyclic_Simulation.queue_length_episode,
        model_data=Model_Simulation.queue_length_episode,
        filename='queue_length_comparison',
        xlabel='Step', 
        ylabel='Queue length (vehicles)'
    )
    visualization.overlayed_plot(
        fixed_time_data=Cyclic_Simulation.avg_wait_episode,
        model_data=Model_Simulation.avg_wait_episode,
        filename='average_wait_length_comparison',
        xlabel='Step', 
        ylabel='Average Wait'
    )
