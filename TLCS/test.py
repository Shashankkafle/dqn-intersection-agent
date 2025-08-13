from dotenv import load_dotenv
import os

load_dotenv(override=True)
print(f"route_file after load_dotenv: {os.getenv('OUTPUT_TRIPS_FILE')}")