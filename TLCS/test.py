from dotenv import load_dotenv
import os
from fixed_duration_calculation import get_durations 
from utils import import_train_configuration, set_sumo, set_train_path
from universal_generator import UniversalTrafficGenerator

# This is a test script just to test code. It is like a rough notebook.
load_dotenv(override=True)
config = import_train_configuration(config_file='training_settings.ini')
output_trips_file = "D:/q-earning/dqn-intersection-agent/TLCS/intersection/test_route.rou.xml"
NET_FILE = os.getenv("NET_FILE")
TrafficGen = UniversalTrafficGenerator(
    NET_FILE,
    output_trips_file,
    sim_end=config['max_steps'],
    vehicle_count=config['n_cars_generated']
)

TrafficGen.generate_routefile(seed=0)
fixed_durations = get_durations(output_trips_file, config['max_steps'])
