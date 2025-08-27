from dotenv import load_dotenv
import os
from fixed_duration_calculation import get_durations 
from utils import import_test_configuration, set_sumo, set_train_path, set_test_path
from universal_generator import UniversalTrafficGenerator
from visualization import Visualization

# This is a test script just to test code. It is like a rough notebook.
load_dotenv(override=True)
config = import_test_configuration(config_file='testing_settings.ini')
model_path, plot_path, comaprision_path = set_test_path(config['models_path_name'], config['model_to_test'])

visualization = Visualization(
       comaprision_path, 
        dpi=96
    )
visualization.save_data(
            data={'a':1,'b':2,'c':[3,4,5]},
            filename='test_data',   
            foldername='test_folder')
     

