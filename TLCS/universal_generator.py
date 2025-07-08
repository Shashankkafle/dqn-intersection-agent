import random
import xml.etree.ElementTree as ET
from sumolib.net import readNet
from itertools import permutations, product
from dotenv import load_dotenv
import os



load_dotenv()

# ---- CONFIG ----
NET_FILE =os.getenv("NET_FILE")
OUTPUT_TRIPS_FILE = os.getenv("OUTPUT_TRIPS_FILE")
if not NET_FILE or not OUTPUT_TRIPS_FILE:
    raise ValueError("Please set the NET_FILE and OUTPUT_TRIPS_FILE environment variables.")
SIM_START = 0
SIM_END = 3600  # in seconds
VEHICLE_RATE = 1  # vehicles per second

# Turning probabilities (from each incoming edge)
# Format: {from_edge: {to_edge: probability, ...}, ...}
TURNING_PROBS = {
    "N2TL": {"TL2S": 1, "TL2E": 0, "TL2W": 0},
    "S2TL": {"TL2N": 1, "TL2E": 0, "TL2W": 0},
    "E2TL": {"TL2W": 1, "TL2N": 0, "TL2S": 0},
    "W2TL": {"TL2E": 1, "TL2N": 0, "TL2S": 0},
}

# Vehicle type
VEHICLE_TYPE = "car"

# ---- MAIN ----

def choose_destination(turning_dict):
    """Randomly select destination edge based on probabilities."""
    to_edges = list(turning_dict.keys())
    probs = list(turning_dict.values())
    return random.choices(to_edges, probs)[0]

def generate_trips(net, trip_rate=1.0):
    trips = []
    trip_id = 0
    time = SIM_START
    while time < SIM_END:
        for from_edge in TURNING_PROBS:
            if from_edge not in net.getEdge(from_edge).getID():
                continue
            to_edge = choose_destination(TURNING_PROBS[from_edge])
            trips.append({
                "id": f"trip{trip_id}",
                "depart": round(time, 2),
                "from": from_edge,
                "to": to_edge,
                "route": f"route_{from_edge}_{to_edge}"
            })
            trip_id += 1
        time += 1.0 / trip_rate
    return trips

def generate_routes(net):
    """Generate all possible routes. NOTE: the junction with the traffic light must have id 'TL'."""
    routes = []
    edges = net.getEdges()
    incomming_edges = []
    outgoing_edges = []
    for edge in edges:
        from_node_id = edge.getFromNode().getID()
        if from_node_id == "TL":
            outgoing_edges.append(edge)
        else:
            incomming_edges.append(edge)
    print(f"Incoming edges: {[edge.getID() for edge in incomming_edges]}")
    print(f"Outgoing edges: {[edge.getID() for edge in outgoing_edges]}")
    possible_routes = []
    for edge_from in incomming_edges:
        for edge_to in outgoing_edges:
            # print(f"Checking route from {edge_from} to {edge_to}")
            if edge_from.getFromNode().getID() == edge_to.getToNode().getID():
                continue    
            possible_routes.append((edge_from, edge_to))
    print(f"Possible routes: {(possible_routes)}",len(possible_routes))
    return possible_routes


def write_trips(trips, output_file,routes):
    root = ET.Element("routes")
    print("Writing trips to XML...")
    for route in routes:
        from_edge = route[0].getID()
        to_edge = route[1].getID()
        ET.SubElement(root, "route", id=f"route_{from_edge}_{to_edge}", edges=f"{from_edge} {to_edge}")
    ET.SubElement(root, "vType", id=VEHICLE_TYPE, accel="2.6", decel="4.5", sigma="0.5", length="5", minGap="2.5", maxSpeed="50")

    for trip in trips:
        ET.SubElement(root, "vehicle", id=trip["id"], depart=str(trip["depart"]), from_=trip["from"], to=trip["to"],route=trip["route"],departLane="random", type=VEHICLE_TYPE)

    tree = ET.ElementTree(root)
    print("element tree created",tree)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    print(f"✅ Trips written to {output_file}")

def main():
    print("Starting trip generation...")
    net = readNet(NET_FILE)
    routes = generate_routes(net)
    trips = generate_trips(net, VEHICLE_RATE)
    write_trips(trips, OUTPUT_TRIPS_FILE,routes)

if __name__ == "__main__":
    main()
