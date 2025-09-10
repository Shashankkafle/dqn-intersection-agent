from model import TrainModel
from tensorflow.keras.utils import plot_model
import numpy as np
import traci

lane_id_to_index = {
    "W2TL_0": 0,
    "W2TL_1": 1,
    "W2TL_2": 2,
    "W2TL_3": 3,
    "N2TL_0": 4,
    "N2TL_1": 5,
    "N2TL_2": 6,
    "N2TL_3": 7,
    "E2TL_0": 8,
    "E2TL_1": 9,
    "E2TL_2": 10,
    "E2TL_3": 11,
    "S2TL_0": 12,
    "S2TL_1": 13,
    "S2TL_2": 14,
    "S2TL_3": 15
}

def _get_state():
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
    # The magic numbber 16 represents the number of states and 19 represents the number of cells per lane
        state = np.zeros((16,19))
        car_list = traci.vehicle.getIDList()

        for car_id in car_list:
            lane_pos = traci.vehicle.getLanePosition(car_id)
            lane_id = traci.vehicle.getLaneID(car_id)
            # lane_pos = 750 - lane_pos  # inversion of lane pos, so if the car is close to the traffic light -> lane_pos = 0 --- 750 = max len of a road
            lane_index = lane_id_to_index.get(lane_id)
            if lane_index is None:
                raise ValueError(f"Unexpected lane ID: {lane_id}")
            cell_index = min(int(lane_pos // 7.5), 18)  # Each cell represents 7.5 meters, max index is 18
            state[lane_index, cell_index] = 1  # Mark the cell as occupied
            print(f"Car {car_id} in lane {lane_id} at position {lane_pos} occupies cell {cell_index} in lane index {lane_index}")
            
        return state





