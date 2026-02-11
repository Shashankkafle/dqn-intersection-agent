from __future__ import absolute_import
from __future__ import print_function

import os
import datetime
from shutil import copyfile

from training_simulation import Simulation
from generator import TrafficGenerator
from memory import Memory
from model import TrainModel
from visualization import Visualization
from utils import import_train_configuration, set_sumo, set_train_path
from universal_generator import UniversalTrafficGenerator



if __name__ == "__main__":

    config = import_train_configuration(config_file='training_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    path = set_train_path(config['models_path_name'])

    Model = TrainModel(
        config['num_layers'], 
        config['width_layers'], 
        config['batch_size'], 
        config['learning_rate'], 
        input_dim= config['state_max_lane_length'] // config['state_block_size'] * config['num_state_lane_groups'], 
        output_dim=config['num_actions']
    )

    Memory = Memory(
        config['memory_size_max'], 
        config['memory_size_min']
    )

    # TrafficGen = TrafficGenerator(
    #     config['max_steps'], 
    #     config['n_cars_generated']
    # )
    flow_rate = config['n_cars_generated'] / config['max_steps']
    NET_FILE = os.getenv("NET_FILE")
    OUTPUT_TRIPS_FILE = os.getenv("OUTPUT_TRIPS_FILE")

    TrafficGen = UniversalTrafficGenerator(
        NET_FILE,
        OUTPUT_TRIPS_FILE,
        sim_end=config['max_steps'],
        vehicle_count= config['n_cars_generated'] 
    )
    route_weights = TrafficGen._route_weights
    visualization = Visualization(
        path, 
        dpi=96
    )
        
    Simulation = Simulation(
        Model,
        Memory,
        TrafficGen,
        sumo_cmd,
        config['gamma'],
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['clearence_interval'],
        config['state_max_lane_length'],
        config['state_block_size'],
        config['num_actions'],
        config['training_epochs'],

    )


    episode = 0
    timestamp_start = datetime.datetime.now()
    
    while episode < config['total_episodes']:
        print('\n----- Episode', str(episode+1), 'of', str(config['total_episodes']))
        epsilon = 1.0 - (episode / config['total_episodes'])  # set the epsilon for this episode according to epsilon-greedy policy
        simulation_time, training_time = Simulation.run(episode, epsilon)  # run the simulation
        print('Simulation time:', simulation_time, 's - Training time:', training_time, 's - Total:', round(simulation_time+training_time, 1), 's')
        if(episode % 20 == 0 and episode != 0):
            temp_path = os.path.join(path, 'episode'+str(episode))
            os.makedirs(temp_path, exist_ok=True)
            temp_visualizaton =Visualization(
                temp_path, 
                dpi=96
            )
            
            temp_visualizaton.save_data_and_plot(data=Simulation.reward_store, filename='reward', xlabel='Episode', ylabel='Cumulative negative reward')
            temp_visualizaton.save_data_and_plot(data=Simulation.cumulative_wait_store, filename='delay', xlabel='Episode', ylabel='Cumulative delay (s)')
            temp_visualizaton.save_data_and_plot(data=Simulation.avg_queue_length_store, filename='queue', xlabel='Episode', ylabel='Average queue length (vehicles)')
            temp_visualizaton.save_data(route_weights, filename='route_weights')
            Model.save_model(temp_path)
        episode += 1

    print("\n----- Start time:", timestamp_start)
    print("----- End time:", datetime.datetime.now())
    print("----- Session info saved at:", path)

    Model.save_model(path)
    copyfile(src='training_settings.ini', dst=os.path.join(path, 'training_settings.ini'))

    visualization.save_data_and_plot(data=Simulation.reward_store, filename='reward', xlabel='Episode', ylabel='Cumulative negative reward')
    visualization.save_data_and_plot(data=Simulation.cumulative_wait_store, filename='delay', xlabel='Episode', ylabel='Cumulative delay (s)')
    visualization.save_data_and_plot(data=Simulation.avg_queue_length_store, filename='queue', xlabel='Episode', ylabel='Average queue length (vehicles)')
    visualization.save_data(route_weights, filename='route_weights')
    copyfile(src='intersection\sumo_config.sumocfg', dst=os.path.join(path, 'sumo_config.sumocfg'))