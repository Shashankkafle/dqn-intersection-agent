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
from multiple_comparision import run_test

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
    for i in range(5):
        n_cars = config['n_cars_generated'] + i*100
        print(f"\n\n\nRunning tests with {n_cars} cars generated.\n\n\n")
        run_test(config=config,TrafficGen=TrafficGen,OUTPUT_TRIPS_FILE=OUTPUT_TRIPS_FILE,n_cars_generated=n_cars, model_number_list=model_number_list)
        n_cars = config['n_cars_generated'] - i*100
        print(f"\n\n\nRunning tests with {n_cars} cars generated.\n\n\n")
        run_test(config=config,TrafficGen=TrafficGen,OUTPUT_TRIPS_FILE=OUTPUT_TRIPS_FILE,n_cars_generated=n_cars, model_number_list=model_number_list)