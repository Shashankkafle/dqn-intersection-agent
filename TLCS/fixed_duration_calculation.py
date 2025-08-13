import os
import sumolib
from dotenv import load_dotenv

# All constant assumptions
PHF = 0.9  # Peak Hourly Factor
S=1800  # Saturation flow rate  = 3600/headway assuming 2 seconds headway

# lane groups in a phase
# PHASE_NS_GREEN 
# PHASE_NSL_GREEN  
# PHASE_EW_GREEN 
# PHASE_EWL_GREEN 
lane_group_to_phase = {
"W_E": "PHASE_EW_GREEN",
"E_W": "PHASE_EW_GREEN",
"N_S": "PHASE_NS_GREEN",
"S_N": "PHASE_NS_GREEN",
"E_S": "PHASE_EWL_GREEN",
"W_N": "PHASE_EWL_GREEN",
"S_E": "PHASE_NSL_GREEN",
"N_W": "PHASE_NSL_GREEN",
}
phase_to_lane_group = {
    "PHASE_NS_GREEN": ["N_S", "S_N"],
    "PHASE_NSL_GREEN": ["N_W", "S_E"],
    "PHASE_EW_GREEN": ["W_E", "E_W"],
    "PHASE_EWL_GREEN": ["E_S", "W_N"]
}
load_dotenv(override=True)
def get_analysis_flow():
 return

def get_durations(route_file,max_steps):
        """
        Function to get the analysis flow rate and durations for each lane group
        """
        # # CAUTION:siulation hours will be accurate only when each step i one second long
        # # if the simulation is not one second per step, this will not be accurate
        simulation_hours = max_steps / 3600

        if not route_file or not os.path.exists(route_file):
            print(f"Route file {route_file} does not exist.")
            raise FileNotFoundError(f"Route file {route_file} does not exist.")
        
        routes = sumolib.xml.parse(route_file, "vehicle")

        lane_group_counts = {}
        for v in routes:
            route_id = v.route
            if route_id in lane_group_counts:
                lane_group_counts[route_id] += 1
            else:
                lane_group_counts[route_id] = 1
        lane_group_flow = {}
        lane_group_to_flow_ratio = {}

        print("vehicle counts")
        for lane_group, count in lane_group_counts.items():
            print(f"{lane_group}: {count} vehicles")
            lane_group_flow[lane_group] = (count/simulation_hours) / PHF 
            lane_group_to_flow_ratio[lane_group] = lane_group_flow[lane_group] / S

        print("flow ratios")
        for lane_group, ratio in lane_group_to_flow_ratio.items():
            print(f"{lane_group}: {ratio} ")
        
        # find critical lane group for each phase
        phase_to_critical_lane = {}
        for phase in phase_to_lane_group:
            lane_groups = phase_to_lane_group[phase]
            critical_lane = lane_groups[0]
            for lane_group in lane_groups:
                print(f"Phase {phase} has lane group {lane_group}")
                if lane_group in lane_group_to_flow_ratio:
                    if( lane_group_to_flow_ratio[lane_group] > lane_group_to_flow_ratio[critical_lane]):
                        critical_lane = lane_group
                else:
                    raise Exception(f"Lane group {lane_group} not found in flow ratios.")
            phase_to_critical_lane[phase] = critical_lane
        print("phase to critical lane",phase_to_critical_lane)
        # sum of critical flow ratios
        sum_critical_flow_ratio = 0
        for phase in phase_to_critical_lane:
            critical_lane = phase_to_critical_lane[phase]
            sum_critical_flow_ratio += lane_group_to_flow_ratio[critical_lane]
        print("sum_critical_flow_ratio", sum_critical_flow_ratio)

        # total cicle lost time(assuming 4s for each phase)
        total_lost_time = 4 * len(phase_to_critical_lane) 
        print("total lost time", total_lost_time)

        # calculate optimal cycle length
        optimal_cycle_length = (1.5 * total_lost_time + 5) / (1-sum_critical_flow_ratio)
        print("optimal cycle length", optimal_cycle_length)

        # calculate min cycle length(assuming Xc=0.9)
        min_cycle_length = (total_lost_time*0.9) / (0.9-sum_critical_flow_ratio)
        print("min cycle length", min_cycle_length)

        # calculate green duration for each phase
        phase_to_green_duration = {}
        Xc = (sum_critical_flow_ratio*optimal_cycle_length)/(optimal_cycle_length - total_lost_time)
        for phase in phase_to_critical_lane:
            critical_lane = phase_to_critical_lane[phase]
            if critical_lane in lane_group_to_flow_ratio:
                critical_lane_flow_ratio = lane_group_to_flow_ratio[critical_lane]
                green_duration = critical_lane_flow_ratio * (optimal_cycle_length / Xc)
                phase_to_green_duration[phase] = green_duration
                print(f"Phase {phase} green duration: {green_duration} seconds")
            else:
                raise Exception(f"Critical lane {critical_lane} not found in flow ratios.")
            
        print("phase to green duration", phase_to_green_duration)
            
        # Assuming fixed durations for green and yellow lights
        green_duration = 30  # seconds
        yellow_duration = 5  # seconds
        
        return  green_duration, yellow_duration
route_file = os.getenv("OUTPUT_TRIPS_FILE")
max_steps = 5400  # Example max steps, adjust as needed
get_durations(route_file, max_steps)