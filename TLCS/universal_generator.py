import numpy as np
import math
import xml.etree.ElementTree as ET

class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated, network_path):
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
        self.network_path = network_path

    def extract_connections(self):
        """
        Extracts all the possibole paths that a vehicle can take in the network.
        This worksonly for a single intersetion network.
        Make sure that the connection is indexed in the traffic light control configuration.
        """
        tree = ET.parse(self.network_path)
        root = tree.getroot()
        for connection in root.findall('connection'):
            from_lane = connection.get('from')
            to_lane = connection.get('to')
            linkIndex = connection.get('linkIndex')
            print(f"Connection from {from_lane} to {to_lane} linkIndex {linkIndex}")
    
    # def generate_routefile(self, seed):
generator = TrafficGenerator(max_steps=1000, n_cars_generated=100, network_path='C:/Users/GIS2025/Q-learning/Deep-QLearning-Agent-for-Traffic-Signal-Control/TLCS/intersection/two_lanes.net.xml')
generator.extract_connections()