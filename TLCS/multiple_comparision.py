from __future__ import absolute_import
from __future__ import print_function

import os
from shutil import copyfile

from fixed_time_sim import Simulation
from universal_generator import UniversalTrafficGenerator
from model import TestModel
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path, import_train_configuration
from fixed_duration_calculation import get_durations 


def run_test(config, TrafficGen,OUTPUT_TRIPS_FILE, n_cars_generated = None, model_number_list =[]):
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    
    
    print("\n\n\n\n\n\n\nconfig['n_cars_generated'] in comparision:", config['n_cars_generated'])
    if n_cars_generated is None:
        n_cars_generated = config['n_cars_generated']


    if len(model_number_list) == 0:
        print("No model numbers provided for evaluation.")
        return
    for model_number in model_number_list:
        print(f"Evaluating model number: {model_number}")
        model_path, plot_path, comaprision_path = set_test_path(config['models_path_name'], model_number)
        model_config = import_train_configuration(config_file=model_path+'/training_settings.ini')
        # print(f"Model configuration: {model_config}")
        config['green_duration'] = model_config['green_duration']
        config['yellow_duration'] = model_config['yellow_duration']
        config['clearence_interval'] = model_config['clearence_interval']
        config['n_cars_generated'] = n_cars_generated
        config['max_steps'] = model_config['max_steps']
        config['model_to_test'] = model_number
        model_path, plot_path, comaprision_path = set_test_path(config['models_path_name'], config['model_to_test'])
        Model = TestModel(
        input_dim=config['num_states'],
        model_path=model_path
        )
        print("starting comparision for model:",model_number)
        print("config values:  \n",config)
    
        visualization = Visualization(
       comaprision_path, 
        dpi=96
        )
        test_ep_count = 1
        cum_avg_wait = 0
        cum_avg_queue_length = 0
        for i in range(test_ep_count):
            route_weights = TrafficGen.generate_routefile(seed=i,vehicle_count=n_cars_generated)
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
            print("Model simulation starting...")
            simulation_time = Model_Simulation.run(i)  # run the simulation
            print("cyclic simulation starting...")
            simulation_time = Cyclic_Simulation.run(i)  # run the simulation
            print('Simulation time:', simulation_time, 's')
            # print('Model - Total cumulative wait time:', Model_Simulation._cum_wait_time_per_vehicle, 's')
            # print('Fixed Time - Total cumulative wait time:', Cyclic_Simulation.cum_wait_time_per_vehicle, 's')
            episode_stats = {}
            episode_stats['model_total_wait'] = sum(Model_Simulation.cum_wait_time_per_vehicle.values())
            episode_stats['fixed_time_total_wait'] = sum(Cyclic_Simulation.cum_wait_time_per_vehicle.values())
            
            episode_stats['model_avg_wait'] = episode_stats['model_total_wait'] / n_cars_generated
            episode_stats['fixed_time_avg_wait'] = episode_stats['fixed_time_total_wait'] / n_cars_generated
            episode_stats['n_cars_generated'] = n_cars_generated
            # print("----- Testing info saved at:", plot_path)
            print("episode_stats:", episode_stats)

            # copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))
            foldername=f'volume_{n_cars_generated}/test_episode{i}'
            visualization.save_data(foldername=foldername,data=Model_Simulation.reward_episode, filename='model_reward', )
            visualization.save_data(foldername=foldername,data=Model_Simulation.total_queue_length_episode, filename='model_queue')
            visualization.save_data(foldername=foldername,data=Model_Simulation.avg_wait_episode, filename='model_average_wait')
            visualization.save_data(foldername=foldername,data=Cyclic_Simulation.reward_episode, filename='fixed_time_reward', )
            visualization.save_data(foldername=foldername,data=Cyclic_Simulation.total_queue_length_episode, filename='tixed_time_queue')
            visualization.save_data(foldername=foldername,data=Cyclic_Simulation.avg_wait_episode, filename='tixed_time_average_wait')
        
            visualization.save_data(
                data=fixed_durations,
                filename='webster_fixed_timings',
                foldername=foldername
            )
            visualization.save_data(
                data=lane_group_counts,
                filename='vehicles_per_lane_group',
                foldername=foldername
            )
            visualization.save_data(
                data=route_weights,
                filename='route_weights',
                foldername=foldername
            )
            visualization.save_data(
                data=Model_Simulation.cum_wait_time_per_vehicle,
                filename='cum_wait_time_per_vehicle_dqn',
                foldername=foldername
            )
            visualization.save_data(
                data=Cyclic_Simulation.cum_wait_time_per_vehicle,
                filename='cum_wait_time_per_vehicle_fixed_time',
                foldername=foldername
            )
            visualization.save_data(
                data=Model_Simulation.phase_change_sequence,
                filename='phase_change_sequence_dqn',
                foldername=foldername
            )
            visualization.save_data(
                data=Cyclic_Simulation.phase_change_sequence,
                filename='phase_change_sequence_fixed_time',
                foldername=foldername
            )
            visualization.save_data(
                data=Model_Simulation._queue_length_episode_by_direction,
                filename='queue_length_by_direction_dqn',
                foldername=foldername
            )
            visualization.save_data(
                data=Cyclic_Simulation._queue_length_episode_by_direction,
                filename='queue_length_by_direction_fixed_time',
                foldername=foldername
            )
            visualization.save_data(
                data=episode_stats,
                filename='episode_stats',
                foldername=foldername
            )
            visualization.save_data(
                data=config,
                filename='training_settings',
                foldername=foldername
            )
            visualization.overlayed_plot(
                fixed_time_data=Cyclic_Simulation.total_queue_length_episode,
                model_data=Model_Simulation.total_queue_length_episode,
                filename='queue_length_comparison',
                xlabel='Step', 
                ylabel='Queue length (vehicles)',
                foldername=foldername
            )
            visualization.overlayed_plot(
                fixed_time_data=Cyclic_Simulation.avg_wait_episode,
                model_data=Model_Simulation.avg_wait_episode,
                filename='average_wait_length_comparison',
                xlabel='Action Step', 
                ylabel='Average Wait',
                foldername=foldername
            )
            visualization.overlayed_plot(
                fixed_time_data=Cyclic_Simulation._reward_episode,
                model_data=Model_Simulation._reward_episode,
                filename='reward_comparison',
                xlabel='Step', 
                ylabel='Reward',
                foldername=foldername
            )
            
            copyfile(src=OUTPUT_TRIPS_FILE, dst=os.path.join(comaprision_path,foldername, 'episode_routes_rou.xml'))


if __name__ == "__main__":
    # List of model numbers to evaluate
    model_number_list = [131] 
    NET_FILE = os.getenv("NET_FILE")
    OUTPUT_TRIPS_FILE = os.getenv("OUTPUT_TRIPS_FILE")
    config = import_test_configuration(config_file='testing_settings.ini')
    n_cars_generated = config['n_cars_generated']
    
    TrafficGen = UniversalTrafficGenerator(
        NET_FILE,
        OUTPUT_TRIPS_FILE,
        sim_end=config['max_steps'],
        vehicle_count= n_cars_generated
        )
    run_test(config=config,TrafficGen=TrafficGen,OUTPUT_TRIPS_FILE=OUTPUT_TRIPS_FILE,model_number_list=model_number_list)
    
