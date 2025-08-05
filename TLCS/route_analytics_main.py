from universal_generator import UniversalTrafficGenerator
from route_analytics import get_analysis_flow
import os
from utils import import_train_configuration

config = import_train_configuration(config_file='training_settings.ini')
flow_rate = config['n_cars_generated'] / config['max_steps']
NET_FILE = os.getenv("NET_FILE")
OUTPUT_TRIPS_FILE = os.getenv("OUTPUT_TRIPS_FILE")
TrafficGen = UniversalTrafficGenerator(
        NET_FILE,
        OUTPUT_TRIPS_FILE,
        sim_end=config['max_steps'],
        vehicle_rate=flow_rate
    )

for i in range(5):
    TrafficGen.generate_routefile(seed=i)
    get_analysis_flow(OUTPUT_TRIPS_FILE,max_steps=config['max_steps'],car_count = config['n_cars_generated'])

