import threading
import time
from fred_communication import FredCommunication
from satellite import Satellite

class SatelliteMover (threading.Thread):
    def __init__(self, name, satellite, delay):
        threading.Thread.__init__(self)
        self.name = name
        self.satellite = satellite
        self.delay = delay
    
    def run(self):
        steps = 1000
        step_length = 5
        while(True):
            for step in range(0, steps):
                next_time = step * step_length
                self.satellite.set_new_position(next_time)
                print("Update:")
                print(f"{self.name}: {str(self.satellite.get_current_position())}")
                print("---------------")
                time.sleep(self.delay)