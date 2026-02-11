import numpy as np

class State:
    def __init__(self, traci, max_lane_length=150, block_size=5, num_lane_groups=3, group_mapping={
            "W2TL_1": 0, "W2TL_0": 0,
            "S2TL_0": 1,
            "E2TL_1": 2, "E2TL_0": 2
        }):
        self._traci = traci
        self._block_size = block_size
        self._max_lane_length = max_lane_length
        self._num_lane_groups = num_lane_groups
        
        # Fixed size for NN input: (150/5) * 3 = 90 elements
        self._cells_per_group = self._max_lane_length // self._block_size
        self.num_states = self._cells_per_group * self._num_lane_groups

        self._group_mapping = group_mapping
        # Pre-calculate the mask once
        self.mask = np.zeros(self.num_states)
        try:
            for lane_id, group_idx in self._group_mapping.items():
                lane_length = self._traci.lane.getLength(lane_id)
                active_cells = int(min(lane_length, self._max_lane_length) // self._block_size)
                start_idx = group_idx * self._cells_per_group
                self.mask[start_idx : start_idx + active_cells] = 1.0
                print(f"Mask for lane {lane_id} (group {group_idx}): cells 0 to {active_cells-1} set to 1")
        except Exception as e:
            print(f"Warning: Could not pre-calculate mask (TraCI not started?): {e}")

    def _get_lane_group(self, lane_id):
        return self._group_mapping.get(lane_id, -1)

    def get_state(self):
        # Always start with a clean state of the fixed size
        state = np.zeros(self.num_states)
        car_list = self._traci.vehicle.getIDList()

        for car_id in car_list:
            lane_id = self._traci.vehicle.getLaneID(car_id)
            lane_group = self._get_lane_group(lane_id)

            if lane_group != -1:
                lane_pos = self._traci.vehicle.getLanePosition(car_id)
                
                lane_length = self._traci.lane.getLength(lane_id)
                
                # Distance to stop bar (0 is closest to the light)
                dist_to_tl = lane_length - lane_pos
                normalized_pos = dist_to_tl / self._max_lane_length
                if dist_to_tl < self._max_lane_length:
                    lane_cell = int(dist_to_tl // self._block_size)
                    
                    # CORRECT FLAT INDEXING: (Group * 30) + Cell
                    state_idx = (lane_group * self._cells_per_group) + lane_cell
                    print(f"\n\n\nCar {car_id} on lane {lane_id} (group {lane_group}) at pos {dist_to_tl} contributes to state index {state_idx}.")
                    
                    if state_idx < self.num_states:
                        state[state_idx] = normalized_pos
                    else:
                        Exception(f"Error: Computed state index {state_idx} out of bounds for car {car_id} on lane {lane_id}")

        # Apply mask and return
        return state * self.mask