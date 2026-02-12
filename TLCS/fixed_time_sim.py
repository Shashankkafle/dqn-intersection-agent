import traci
import numpy as np
import random
import timeit
import os

# phase codes based on environment.net.xml
PHASE_1_GREEN = 0  # action 0 code 00
PHASE_1_YELLOW = 1
PHASE_2_GREEN = 2  # action 1 code 01
PHASE_2_YELLOW = 3
PHASE_3_GREEN = 4  # action 2 code 10
PHASE_3_YELLOW = 5

action_number_to_phase_name = {
    0: "PHASE_1_GREEN",
    1: "PHASE_2_GREEN",
    2: "PHASE_3_GREEN",

}
action_number_to_phase_number = {
    0: PHASE_1_GREEN,
    1: PHASE_2_GREEN,
    2: PHASE_3_GREEN,

}



class Simulation:
    def __init__(self, Model, TrafficGen, sumo_cmd, max_steps, green_duration, yellow_duration,clearence_duration, num_states, num_actions, fixed_time=False, durations={}):
        self._Model = Model
        self._TrafficGen = TrafficGen
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._clearence_duration = clearence_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._reward_episode = []
        self._avg_wait_episode = []
        self._queue_length_episode = []
        self._fixed_time = fixed_time  # Flag to indicate if fixed time simulation is used
        self._durations = durations  # Dictionary to hold fixed durations for each action if provided


    def run(self, episode, epsilon):
        """
        Runs the testing simulation
        """
        start_time = timeit.default_timer()
        traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits
        self._step = 0
        self._waiting_times = {}
        old_total_wait = 0
        old_action = -1 # dummy init

        while self._step < self._max_steps:

            # get current state of the intersection
            current_state = self._get_state()
            print("step:", self._step)
            print("state:", current_state)
            # calculate reward of previous action: (change in cumulative waiting time between actions)
            # waiting time = seconds waited by a car since the spawn in the environment, cumulated for every car in incoming lanes
            current_total_wait,current_average_wait = self._collect_waiting_times()
            reward = old_total_wait - current_total_wait
            if self._fixed_time:
                action = (old_action + 1) % self._num_actions # cyclical action
                print("fixed time",action)

            else:
                # choose the light phase to activate, based on the current state of the intersection
                action = self._choose_action(current_state)
                print("model based",action)


            # if the chosen phase is different from the last phase, activate the yellow phase
            if self._step != 0 and old_action != action:
                self._set_yellow_phase(old_action)
                self._simulate(self._yellow_duration)
                self._set_clearence_phase()
                self._simulate(self._clearence_duration)

            # execute the phase selected before
            self._set_green_phase(action)
            if self._fixed_time:
                phase_name = action_number_to_phase_name.get(action)
                green_duration = self._durations.get(phase_name)
                print("self._durations",self._durations,"action",phase_name,)
                print(f"Using fixed green duration: {green_duration} seconds for action {action}")
            else:
                # use the configured green duration
                green_duration = self._green_duration
            self._simulate(self._green_duration)

            # saving variables for later & accumulate reward
            old_action = action
            old_total_wait = current_total_wait

            self._reward_episode.append(reward)
            self._avg_wait_episode.append(current_average_wait)


        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time


    def _simulate(self, steps_todo):
        """
        Execute steps in sumo while gathering statistics
        """
        if (self._step + steps_todo) >= self._max_steps:  # do not do more steps than the maximum allowed number of steps
            steps_todo = self._max_steps - self._step

        while steps_todo > 0:
            traci.simulationStep()  # simulate 1 step in sumo
            self._step += 1 # update the step counter
            steps_todo -= 1
            queue_length = self._get_queue_length() 
            self._queue_length_episode.append(queue_length)


    def _collect_waiting_times(self):
        """
        Retrieve the waiting time of every car in the incoming roads
        """
        incoming_roads = ["E2TL", "W2TL", "S2TL"]
        car_list = traci.vehicle.getIDList()
        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)  # get the road id where the car is located
            if road_id in incoming_roads:  # consider only the waiting times of cars in incoming roads
                self._waiting_times[car_id] = wait_time
            else:
                if car_id in self._waiting_times: # a car that was tracked has cleared the intersection
                    del self._waiting_times[car_id] 
        total_waiting_time = sum(self._waiting_times.values())
        average_waiting_time = total_waiting_time / len(self._waiting_times) if self._waiting_times else 0
        print("total_waiting_time in generator",total_waiting_time)
        return total_waiting_time, average_waiting_time


    def _choose_action(self, state):
        """
        Pick the best action known based on the current state of the env
        """
        return np.argmax(self._Model.predict_one(state))



    def _set_yellow_phase(self, old_action):
        """
        Activate the correct yellow light combination in sumo
        """
        yellow_phase_code = old_action * 2 + 1 # obtain the yellow phase code, based on the old action (ref on environment.net.xml)
        traci.trafficlight.setPhase("TL", yellow_phase_code)

    def _set_clearence_phase(self):
        """
        Activate the correct yellow light combination in sumo
        """
        clearence_phase_code = 6 # CAUTION: make sure this matches the network file
        traci.trafficlight.setPhase("TL", clearence_phase_code)

    def _set_green_phase(self, action_number):
        """
        Activate the correct green light combination in sumo
        """
        if action_number == 0:
            traci.trafficlight.setPhase("TL", PHASE_1_GREEN)
        elif action_number == 1:
            traci.trafficlight.setPhase("TL", PHASE_2_GREEN)
        elif action_number == 2:
            traci.trafficlight.setPhase("TL", PHASE_3_GREEN)
        else:
            raise Exception("Error: action number not recognized")


    def _get_queue_length(self):
        """
        Retrieve the number of cars with speed = 0 in every incoming lane
        """
        halt_S = traci.edge.getLastStepHaltingNumber("S2TL")
        halt_E = traci.edge.getLastStepHaltingNumber("E2TL")
        halt_W = traci.edge.getLastStepHaltingNumber("W2TL")
        queue_length =   halt_S + halt_E + halt_W
        return queue_length


    def _get_state(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        car_list = traci.vehicle.getIDList()

        for car_id in car_list:
            lane_pos = traci.vehicle.getLanePosition(car_id)
            lane_id = traci.vehicle.getLaneID(car_id)
            lane_length = traci.lane.getLength(lane_id)
            lane_pos = lane_length - lane_pos  # inversion of lane pos, so if the car is close to the traffic light -> lane_pos = 0 --- 750 = max len of a road

            # distance in meters from the traffic light -> mapping into cells
            if lane_pos < 5:
                lane_cell = 0
            elif lane_pos < 10:
                lane_cell = 1
            elif lane_pos < 15:
                lane_cell = 2
            elif lane_pos < 20:
                lane_cell = 3
            elif lane_pos < 25:
                lane_cell = 4
            elif lane_pos < 30:
                lane_cell = 5
            elif lane_pos < 35:
                lane_cell = 6
            elif lane_pos <= 40:
                lane_cell = 7
            elif lane_pos <= 45:
                lane_cell = 8
            elif lane_pos <= 50:
                lane_cell = 9
            else:
                lane_cell = None 

            # for 4 leanes with left green
            # finding the lane where the car is located 
            if lane_id ==  lane_id == "W2TL_1" or lane_id == "W2TL_0":
                lane_group = 0
            elif lane_id == "S2TL_0":
                lane_group = 1
            elif lane_id ==  lane_id == "E2TL_1" or lane_id == "E2TL_0":
                lane_group = 2
            else:
                lane_group = -1

            if  lane_cell is None:
                valid_car = False  # flag for not detecting cars crossing the intersection or driving away from it
            elif lane_group >= 1 and lane_group <= 2:
                car_position = int(str(lane_group) + str(lane_cell))  # composition of the two postion ID to create a number in interval 0-79
                valid_car = True
            elif lane_group == 0:
                car_position = lane_cell
                valid_car = True
            else:
                valid_car = False  # flag for not detecting cars crossing the intersection or driving away from it

            if valid_car:
                state[car_position] = 1  # write the position of the car car_id in the state array in the form of "cell occupied"

        return state


    def _replay(self):
        """
        Retrieve a group of samples from the memory and for each of them update the learning equation, then train
        """
        batch = self._Memory.get_samples(self._Model.batch_size)

        if len(batch) > 0:  # if the memory is full enough
            states = np.array([val[0] for val in batch])  # extract states from the batch
            next_states = np.array([val[3] for val in batch])  # extract next states from the batch

            # prediction
            q_s_a = self._Model.predict_batch(states)  # predict Q(state), for every sample
            q_s_a_d = self._Model.predict_batch(next_states)  # predict Q(next_state), for every sample

            # setup training arrays
            x = np.zeros((len(batch), self._num_states))
            y = np.zeros((len(batch), self._num_actions))

            for i, b in enumerate(batch):
                state, action, reward, _ = b[0], b[1], b[2], b[3]  # extract data from one sample
                current_q = q_s_a[i]  # get the Q(state) predicted before
                current_q[action] = reward + self._gamma * np.amax(q_s_a_d[i])  # update Q(state, action)
                x[i] = state
                y[i] = current_q  # Q(state) that includes the updated action value

            self._Model.train_batch(x, y)  # train the NN


    def _save_episode_stats(self):
        """
        Save the stats of the episode to plot the graphs at the end of the session
        """
        self._reward_store.append(self._sum_neg_reward)  # how much negative reward in this episode
        self._cumulative_wait_store.append(self._sum_waiting_time)  # total number of seconds waited by cars in this episode
        self._avg_queue_length_store.append(self._sum_queue_length / self._max_steps)  # average number of queued cars per step, in this episode


    @property
    def queue_length_episode(self):
        return self._queue_length_episode


    @property
    def reward_episode(self):
        return self._reward_episode

    @property
    def avg_wait_episode(self):
        return self._avg_wait_episode



