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
    
    visualization = Visualization(
       comaprision_path, 
        dpi=96
    )
     
    test_ep_count = 3
    cum_avg_wait = 0
    cum_avg_queue_length = 0
    for i in range(test_ep_count):
        route_weights = TrafficGen.generate_routefile(seed=i)
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
        print('Model - Total cumulative wait time:', Model_Simulation._cum_wait_time_per_vehicle, 's')
        print('Fixed Time - Total cumulative wait time:', Cyclic_Simulation.cum_wait_time_per_vehicle, 's')
        episode_stats = {}
        episode_stats['model_total_wait'] = sum(Model_Simulation.cum_wait_time_per_vehicle.values())
        episode_stats['fixed_time_total_wait'] = sum(Cyclic_Simulation.cum_wait_time_per_vehicle.values())
        
        episode_stats['model_avg_wait'] = episode_stats['model_total_wait'] / config['n_cars_generated']
        episode_stats['fixed_time_avg_wait'] = episode_stats['fixed_time_total_wait'] / config['n_cars_generated']
        episode_stats['n_cars_generated'] = config['n_cars_generated']
        # print("----- Testing info saved at:", plot_path)

        copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

        visualization.save_data(foldername=f'test_episode{i}',data=Model_Simulation.reward_episode, filename='model_reward', )
        visualization.save_data(foldername=f'test_episode{i}',data=Model_Simulation.queue_length_episode, filename='model_queue')
        visualization.save_data(foldername=f'test_episode{i}',data=Model_Simulation.avg_wait_episode, filename='model_average_wait')
        visualization.save_data(foldername=f'test_episode{i}',data=Cyclic_Simulation.reward_episode, filename='fixed_time_reward', )
        visualization.save_data(foldername=f'test_episode{i}',data=Cyclic_Simulation.queue_length_episode, filename='tixed_time_queue')
        visualization.save_data(foldername=f'test_episode{i}',data=Cyclic_Simulation.avg_wait_episode, filename='tixed_time_average_wait')
    
        visualization.save_data(
            data=fixed_durations,
            filename='webster_fixed_timings',
            foldername=f'test_episode{i}'
        )
        visualization.save_data(
            data=lane_group_counts,
            filename='vehicles_per_lane_group',
            foldername=f'test_episode{i}'
        )
        visualization.save_data(
            data=route_weights,
            filename='route_weights',
            foldername=f'test_episode{i}'
        )
        visualization.save_data(
            data=Model_Simulation.cum_wait_time_per_vehicle,
            filename='cum_wait_time_per_vehicle_dqn',
            foldername=f'test_episode{i}'
        )
        visualization.save_data(
            data=Model_Simulation.cum_wait_time_per_vehicle,
            filename='cum_wait_time_per_vehicle_fixed_time',
            foldername=f'test_episode{i}'
        )
        visualization.save_data(
            data=episode_stats,
            filename='episode_stats',
            foldername=f'test_episode{i}'
        )
        visualization.overlayed_plot(
            fixed_time_data=Cyclic_Simulation.queue_length_episode,
            model_data=Model_Simulation.queue_length_episode,
            filename='queue_length_comparison',
            xlabel='Step', 
            ylabel='Queue length (vehicles)',
            foldername=f'test_episode{i}'
        )
        visualization.overlayed_plot(
            fixed_time_data=Cyclic_Simulation.avg_wait_episode,
            model_data=Model_Simulation.avg_wait_episode,
            filename='average_wait_length_comparison',
            xlabel='Action Step', 
            ylabel='Average Wait',
            foldername=f'test_episode{i}'
        )
        visualization.overlayed_plot(
            fixed_time_data=Cyclic_Simulation._reward_episode,
            model_data=Model_Simulation._reward_episode,
            filename='reward_comparison',
            xlabel='Step', 
            ylabel='Reward',
            foldername=f'test_episode{i}'
        )
