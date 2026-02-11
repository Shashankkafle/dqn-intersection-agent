from training_simulation import Simulation
from state import State
import traci

sumoCmd = ["sumo-gui", "-c", "intersection/sumo_config.sumocfg"]

def test():
    try:
        traci.start(sumoCmd)
        state = State(traci)
        
        # Run a few steps to ensure vehicles are loaded
        for _ in range(100000):
            traci.simulationStep()
            current_state = state.get_state()
            print("----- Step -----")
            print("step:", traci.simulation.getTime())
            print("\nCurrent State:", current_state)
    except Exception as e:
        print(f"Captured Error: {e}")
    
test()