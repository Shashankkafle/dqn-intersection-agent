import random
import xml.etree.ElementTree as ET
from sumolib.net import readNet
from itertools import permutations, product
from dotenv import load_dotenv
import os



load_dotenv()

class UniversalTrafficGenerator:
    """A class to generate traffic trips for SUMO based on a given network."""

    def __init__(self, net_file, output_trips_file, sim_start=0, sim_end=3600, vehicle_rate=1):
        self._net_file = net_file
        self._output_trips_file = output_trips_file
        self._sim_start = sim_start
        self._sim_end = sim_end
        self._vehicle_rate = vehicle_rate
        # Pass as an arguement later
        # self._NET_FILE = os.getenv("NET_FILE")
        # self._OUTPUT_TRIPS_FILE = os.getenv("OUTPUT_TRIPS_FILE")
        self._VEHICLE_TYPE = "car"
        self._incomming_edges = []
        self._outgoing_edges = []
        self._ROUTE_IDS = []
    

    def _routeIdFromEdges(from_edge, to_edge):
        """Generate a route ID from two edges."""
        return f"route_{from_edge}_{to_edge}"

    def _generate_trips(self, net,trip_rate=2.0):
        trips = []
        trip_id = 0
        weights =[]
        time = self._sim_start

        for route in self._ROUTE_IDS:
            print(f"Enter weight for {route}")
            input_weight = float(input(f"Weight for {route}: "))
            weights.append(input_weight)
        tripIDs = random.choices(self._ROUTE_IDS, weights=weights, k=int((self._SIM_END-self._SIM_START) * trip_rate))
        for time, route_id in enumerate(tripIDs):
            trips.append({
                "route": f"{str(route_id)}",
                "depart": str(time),
                "id": f"trip_{time}",
            })
        return trips


    def _generate_routes(self,net):
        """Generate all possible routes. NOTE: the junction with the traffic light must have id 'TL'."""
        routes = []
        edges = net.getEdges()
        for edge in edges:
            from_node_id = edge.getFromNode().getID()
            if from_node_id == "TL":
                self._outgoing_edges.append(edge)
            else:
                self._incomming_edges.append(edge)
        print(f"Incoming edges: {[edge.getID() for edge in self._incomming_edges]}")
        print(f"Outgoing edges: {[edge.getID() for edge in self._outgoing_edges]}")
        possible_routes = []
        for edge_from in self._incomming_edges:
            for edge_to in self._outgoing_edges:
                # print(f"Checking route from {edge_from} to {edge_to}")
                if edge_from.getFromNode().getID() == edge_to.getToNode().getID():
                    continue    
                possible_routes.append((edge_from, edge_to))
                self._ROUTE_IDS.append(self._routeIdFromEdges(edge_from.getID(), edge_to.getID()))
        print(f"Possible routes: {(possible_routes)}",len(possible_routes))
        return possible_routes


    def _write_trips(self,trips):
        root = ET.Element("routes")
        print("Writing trips to XML...")
        for route in self.routes:
            from_edge = route[0].getID()
            to_edge = route[1].getID()
            ET.SubElement(root, "route", id=self._routeIdFromEdges(from_edge, to_edge), edges=f"{from_edge} {to_edge}")
        ET.SubElement(root, "vType", id=self._VEHICLE_TYPE, accel="2.6", decel="4.5", sigma="0.5", length="5", minGap="2.5", maxSpeed="50")

        for trip in trips:
            ET.SubElement(root, "vehicle", id=trip["id"],depart=trip["depart"], route=trip["route"],departLane="random",departSpeed="10", type=VEHICLE_TYPE)

        tree = ET.ElementTree(root)
        print("element tree created",tree)
        tree.write(self._output_trips_file, encoding="UTF-8", xml_declaration=True)
        print(f"✅ Trips written to {self._output_trips_fileoutput_file}")
    
    def generate_route_file(self):
        print("Starting trip generation...")
        net = readNet(self._net_file)
        routes = self._generate_routes(net)
        trips = self._generate_trips(net, self._vehicle_rate)
        self._write_trips(self,trips)


    
# SIM_START = 0
# SIM_END = 3600  # in seconds
# VEHICLE_RATE = 1  # vehicles per second
# incomming_edges = []
# outgoing_edges = []
# ROUTE_IDS = []

# # Vehicle type
# VEHICLE_TYPE = "car"

# # ---- MAIN ----

# def routeIdFromEdges(from_edge, to_edge):
#     """Generate a route ID from two edges."""
#     return f"route_{from_edge}_{to_edge}"

# def choose_destination(turning_dict):
#     """Randomly select destination edge based on probabilities."""
#     to_edges = list(turning_dict.keys())
#     probs = list(turning_dict.values())
#     return random.choices(to_edges, probs)[0]

# def generate_trips(net,trip_rate=2.0):
#     trips = []
#     trip_id = 0
#     weights =[]
#     time = SIM_START

#     for route in ROUTE_IDS:
#         print(f"Enter weight for {route}")
#         input_weight = float(input(f"Weight for {route}: "))
#         weights.append(input_weight)
#     tripIDs = random.choices(ROUTE_IDS, weights=weights, k=int((SIM_END-SIM_START) * trip_rate))
#     for time, route_id in enumerate(tripIDs):
#         trips.append({
#             "route": f"{str(route_id)}",
#             "depart": str(time),
#             "id": f"trip_{time}",
#         })
#     return trips


# def generate_routes(net):
#     """Generate all possible routes. NOTE: the junction with the traffic light must have id 'TL'."""
#     routes = []
#     edges = net.getEdges()
#     for edge in edges:
#         from_node_id = edge.getFromNode().getID()
#         if from_node_id == "TL":
#             outgoing_edges.append(edge)
#         else:
#             incomming_edges.append(edge)
#     print(f"Incoming edges: {[edge.getID() for edge in incomming_edges]}")
#     print(f"Outgoing edges: {[edge.getID() for edge in outgoing_edges]}")
#     possible_routes = []
#     for edge_from in incomming_edges:
#         for edge_to in outgoing_edges:
#             # print(f"Checking route from {edge_from} to {edge_to}")
#             if edge_from.getFromNode().getID() == edge_to.getToNode().getID():
#                 continue    
#             possible_routes.append((edge_from, edge_to))
#             ROUTE_IDS.append(routeIdFromEdges(edge_from.getID(), edge_to.getID()))
#     print(f"Possible routes: {(possible_routes)}",len(possible_routes))
#     return possible_routes


# def write_trips(trips, output_file,routes):
#     root = ET.Element("routes")
#     print("Writing trips to XML...")
#     for route in routes:
#         from_edge = route[0].getID()
#         to_edge = route[1].getID()
#         ET.SubElement(root, "route", id=routeIdFromEdges(from_edge, to_edge), edges=f"{from_edge} {to_edge}")
#     ET.SubElement(root, "vType", id=VEHICLE_TYPE, accel="2.6", decel="4.5", sigma="0.5", length="5", minGap="2.5", maxSpeed="50")

#     for trip in trips:
#         ET.SubElement(root, "vehicle", id=trip["id"],depart=trip["depart"], route=trip["route"],departLane="random",departSpeed="10", type=VEHICLE_TYPE)

#     tree = ET.ElementTree(root)
#     print("element tree created",tree)
#     tree.write(output_file, encoding="UTF-8", xml_declaration=True)
#     print(f"✅ Trips written to {output_file}")


# def main():
#     print("Starting trip generation...")
#     net = readNet(NET_FILE)
#     routes = generate_routes(net)
#     trips = generate_trips(net, VEHICLE_RATE)
#     write_trips(trips, OUTPUT_TRIPS_FILE,routes)

# if __name__ == "__main__":
#     main()
