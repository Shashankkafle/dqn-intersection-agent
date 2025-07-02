import random
import xml.etree.ElementTree as ET
from sumolib.net import readNet

# ---- CONFIG ----
NET_FILE = "C:/Users/GIS2025/Q-learning/Deep-QLearning-Agent-for-Traffic-Signal-Control/TLCS/intersection/two_lanes.net.xml"
OUTPUT_TRIPS_FILE = "intersection_trips.xml"
SIM_START = 0
SIM_END = 3600  # in seconds
VEHICLE_RATE = 1  # vehicles per second

# Turning probabilities (from each incoming edge)
# Format: {from_edge: {to_edge: probability, ...}, ...}
TURNING_PROBS = {
    "N2TL": {"TL2S": 0.6, "TL2E": 0.2, "TL2W": 0.2},
    "S2TL": {"TL2N": 0.6, "TL2E": 0.2, "TL2W": 0.2},
    "E2TL": {"TL2W": 0.6, "TL2N": 0.2, "TL2S": 0.2},
    "W2TL": {"TL2E": 0.6, "TL2N": 0.2, "TL2S": 0.2},
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
                "to": to_edge
            })
            trip_id += 1
        time += 1.0 / trip_rate
    return trips

def write_trips(trips, output_file):
    root = ET.Element("routes")
    ET.SubElement(root, "vType", id=VEHICLE_TYPE, accel="2.6", decel="4.5", sigma="0.5", length="5", minGap="2.5", maxSpeed="50")

    for trip in trips:
        ET.SubElement(root, "trip", id=trip["id"], depart=str(trip["depart"]), from_=trip["from"], to=trip["to"], type=VEHICLE_TYPE)

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    print(f"✅ Trips written to {output_file}")

def main():
    net = readNet(NET_FILE)
    trips = generate_trips(net, VEHICLE_RATE)
    write_trips(trips, OUTPUT_TRIPS_FILE)

if __name__ == "__main__":
    main()
