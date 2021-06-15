import threading
import time
from fred_communication import FredCommunication
from satellite import Satellite
import logging

class SatelliteMover (threading.Thread):
    def __init__(self, name, satellite, delay):
        threading.Thread.__init__(self)
        logging.basicConfig(filename='/logs/' + name + '.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        self.logger = logging.getLogger(f'{name}_mover')
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
                self.logger.info("Update:")
                self.logger.info(f"{self.name}: {str(self.satellite.get_current_position())}")
                self.logger.info("---------------")
                time.sleep(self.delay)
