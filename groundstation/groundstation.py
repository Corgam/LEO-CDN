from typing import List
import numpy as np
import requests


class GroundStation:
    def __init__(
        self,
        id: int,
        file_order: List[int],
        p: float,
        population: int,
        coordinator_host: str,
    ):
        self.id = id
        self.file_order = file_order
        self.p = p
        self.population = population
        self.coordinator_host = coordinator_host

    def query_best_satellite(self):
        response = requests.get(f"{self.coordinator_host}/best_satellite/{self.id}")
        response.raise_for_status()
        best_satellite_host = response.text
        return best_satellite_host

    def send_file_request_to_satellite(self, file_id: int, satellite_host: str):
        response = requests.get(f"{satellite_host}/{file_id}")
        response.raise_for_status()
        data = response.text
        return data

    def send_random_file_requests(self, num: int = 1):
        file_indices = np.random.geometric(self.p, num)
        best_satellite_host = self.query_best_satellite()
        for file_ind in file_indices:
            if file_ind >= len(self.file_order):
                print(f"Sat {self.id}: Skipping unlikely file with index {file_ind}...")
                continue
            file_id = self.file_order[file_ind]
            print(f"Sat {self.id}: Querying file {file_id}...")
            self.send_file_request_to_satellite(file_id, best_satellite_host)
