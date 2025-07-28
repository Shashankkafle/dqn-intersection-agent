import random
import xml.etree.ElementTree as ET
from sumolib.net import readNet
from itertools import permutations, product
from dotenv import load_dotenv
import os



load_dotenv()

class UniversalTrafficGenerator:
    """A class to generate traffic trips for SUMO based on a given network."""

    def __init__(self, net_file, output_trips_file, sim_end=3600, vehicle_rate=1):
        self._net_file = net_file
        self._output_trips_file = output_trips_file
        self._sim_start = 0
        self._sim_end = sim_end
        self._vehicle_rate = vehicle_rate
        self._VEHICLE_TYPE = "car"
        self._possible_routes = []
        self._incomming_edges = []
        self._outgoing_edges = []
        self._ROUTE_IDS = []
        self._net = readNet(self._net_file)
        self._route_weights = []
    

    def _routeIdFromEdges(self,from_edge, to_edge):
        """Generate a route ID from two edges."""
        return f"route_{from_edge}_{to_edge}"

    def _generate_trips(self,seed):
        trips = []
        trip_id = 0
        time = self._sim_start
        print("self._ROUTE_IDS, self._ROUTE_IDS == []",self._ROUTE_IDS, self._ROUTE_IDS == [])
        print("self._sim_start,self._sim_end, self._vehicle_rate",self._sim_start,self._sim_end, self._vehicle_rate,((self._sim_end-self._sim_start) * self._vehicle_rate))
        if not self._ROUTE_IDS or self._ROUTE_IDS == []:
            print("Generating routes...")
            self._generate_routes()
            for route in self._ROUTE_IDS:
                print(f"Enter weight for {route}")
                input_weight = float(input(f"Weight for {route}: "))
                self._route_weights.append(input_weight)
        
        random.seed(seed)
        vehicle_Count = int((self._sim_end-self._sim_start) * self._vehicle_rate)
        tripIDs = random.choices(self._ROUTE_IDS, weights= self._route_weights, k=vehicle_Count)
        print("trip ids length",len(tripIDs))
        time_increment = (self._sim_end - self._sim_start) / vehicle_Count
        for time_count, route_id in enumerate(tripIDs):
            trips.append({
                "route": f"{str(route_id)}",
                "depart": str(time_count * time_increment),
                "id": f"trip_{time_count}",
            })
        return trips


    def _generate_routes(self):
        """Generate all possible routes. NOTE: the junction with the traffic light must have id 'TL'."""
        routes = []
        edges = self._net.getEdges()
        for edge in edges:
            from_node_id = edge.getFromNode().getID()
            if from_node_id == "TL":
                self._outgoing_edges.append(edge)
            else:
                self._incomming_edges.append(edge)
        print(f"Incoming edges: {[edge.getID() for edge in self._incomming_edges]}")
        print(f"Outgoing edges: {[edge.getID() for edge in self._outgoing_edges]}")
        for edge_from in self._incomming_edges:
            for edge_to in self._outgoing_edges:
                # print(f"Checking route from {edge_from} to {edge_to}")
                if edge_from.getFromNode().getID() == edge_to.getToNode().getID():
                    continue    
                self._possible_routes.append((edge_from, edge_to))
                self._ROUTE_IDS.append(self._routeIdFromEdges(edge_from.getID(), edge_to.getID()))
        print(f"Possible routes: {(self._possible_routes)}",len(self._possible_routes))


    def _write_trips(self,trips):
        root = ET.Element("routes")
        print("Writing trips to XML...")
        for route in self._possible_routes:
            from_edge = route[0].getID()
            to_edge = route[1].getID()
            ET.SubElement(root, "route", id=self._routeIdFromEdges(from_edge, to_edge), edges=f"{from_edge} {to_edge}")
        ET.SubElement(root, "vType", id=self._VEHICLE_TYPE, accel="2.6", decel="4.5", sigma="0.5", length="5", minGap="2.5", maxSpeed="50")

        for trip in trips:
            ET.SubElement(root, "vehicle", id=trip["id"],depart=trip["depart"], route=trip["route"],departLane="random",departSpeed="10", type=self._VEHICLE_TYPE)

        tree = ET.ElementTree(root)
        print("element tree created",tree)
        tree.write(self._output_trips_file, encoding="UTF-8", xml_declaration=True)
        print(f"✅ Trips written to {self._output_trips_file}")
    
    def generate_routefile(self,seed):
        print("Starting trip generation...")
        # routes = self.generate_routes()
        trips = self._generate_trips(seed)
        self._write_trips(trips)


    
