#####################
## Ground Stations ##
#####################

import http.client
import json
import math
import threading
from concurrent.futures import as_completed

# Importing needed libraries
import numpy as np
import pandas as pd
import toml
from requests_futures.sessions import FuturesSession


# This class holds all the information about a single HTTP Request.
class HTTPRequest:
    def __init__(self, URL, heads):
        self.URL = URL
        self.heads = heads

    # Sets the URL and heads dic from given string. No error check.
    @classmethod
    def fromString(self, reqString):
        lines = str(reqString).split("\n")
        # Prepare url
        url = lines[0]
        url = url.replace("GET ", "")
        url = url.replace(" HTTP/1.1", "")
        # Prepeare headers
        heads = {}
        for line in lines:
            if line == lines[0] or line == "":
                continue
            else:
                # Fill in the headers
                parts = line.split(": ")
                heads[parts[0]] = parts[1]
        return HTTPRequest(url, heads)


# This class holds information about one groundstation
class GST:
    def __init__(self, id, latitude, longitude, country, numberOfRequests):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.country = country
        self.numberOfRequests = numberOfRequests


#########################
## Internal functions  ##
#########################

# Load the GSTs info into a list
def loadGSTsInfo(config):
    gstsList = list()
    # Treat each line as new object
    df_gst = pd.read_csv("/gsts.csv")

    total_population = df_gst.population.sum()
    for index, gst in df_gst.iterrows():
        gstsList.append(
            GST(
                gst.id,
                float(gst.lat),
                float(gst.lng),
                gst.country,
                # TODO: make number of requests (per second?) depend on population
                math.ceil(
                    (gst.population / total_population)
                    * config["workload"]["num_requests_per_step"]
                ),
            )
        )
    return gstsList


# Create all threads and all GSTs
def createGSTs(config, gstsList):
    # Number of threads to create
    threadsNumber = config["gsts"]["number_of_threads"]
    # Split the gsts into n threads
    splittedGST = 0
    numberOfGSTinThread = math.ceil(len(gstsList) / threadsNumber)
    threadsLists = list()
    while splittedGST < len(gstsList):
        # Create a list that will hold groundstations for one thread
        newThreadList = list()
        for x in range(numberOfGSTinThread):
            # Look out for the out of bounds error
            if splittedGST + x < len(gstsList):
                newThreadList.append(gstsList[splittedGST + x])
        splittedGST = splittedGST + numberOfGSTinThread
        # Add the list to the list of lists
        threadsLists.append(newThreadList)
    threads = list()
    # Create thread for each list of the gsts
    for gstList in threadsLists:
        threads.append(
            threading.Thread(
                target=sendRequestsForAllGsts,
                args=(
                    config,
                    gstList,
                ),
            )
        )
    # Start threads
    for thread in threads:
        thread.start()


# Reads the file order for generator of requests
def readFileOrder(gstID):
    # Read the file order json
    with open("./file_orders.json") as f:
        fileOrderJSON = json.load(f)
        # Return file order for specific GST
        return fileOrderJSON[str(gstID)]


# Generate requests based on new workload
def generateRequests(gstID, p, numberOfRequests):
    reqsList = list()
    # Read the file order
    fileOrder = readFileOrder(gstID)
    # Generate indicies of files
    file_indices = np.random.geometric(p, numberOfRequests)
    for file_ind in file_indices:
        # Skip unlikely file
        if file_ind >= len(fileOrder):
            continue
        # Create new request
        file_id = fileOrder[file_ind]
        req = f"GET /{file_id} HTTP/1.1"
        reqsList.append(HTTPRequest.fromString(req))
    reqsList.append(HTTPRequest.fromString("GET /mostPopularFile HTTP/1.1"))
    return reqsList


# Choose the best satelitte to send the HTTP requests to, by communicating with the coordinator
def getTheBestSatellite(session, id):
    # Communicate with the Coordinator to choose the best satellite.
    future = session.get(f"http://172.26.4.1:9001/best_satellite/{id}")
    resp = future.result()
    data = resp.text
    if data != "Invalid GST ID":
        # Return the ip and port to the best satellite
        print(
            f"[{threading.current_thread().name}]Answer from coordinator received: {data}.\n"
        )
        return data
    else:
        return -1


def sendRequests(session, gst, reqsList):
    responses = []

    # Generate the requests
    reqsList = generateRequests(
        gst.id, config["workload"]["geometric_p"], gst.numberOfRequests
    )
    # Create a connection to the best satellite
    print(
        f"[{threading.current_thread().name}]Sending query to coordinator for the best satellite...\n"
    )
    bestSat = getTheBestSatellite(session, gst.id)
    if bestSat == -1:
        print(f"[{threading.current_thread().name}]Invalid GST ID...\n")
        return
    # Send all requests
    print(
        f"[{threading.current_thread().name}]Sending all {len(reqsList)} HTTP requests...\n"
    )
    for req in reqsList:
        # Send the request in an async fashion
        responses.append(session.get("http://" + bestSat + req.URL))
    return responses


# Send all requests to the best satellite
def sendRequestsForAllGsts(config, gstList):
    responses = []
    session = FuturesSession()
    for gst in gstList:
        # Generate the requests
        reqsList = generateRequests(
            gst.id, config["workload"]["geometric_p"], gst.numberOfRequests
        )
        responses += sendRequests(session, gst, reqsList)

    # Read all of the responses (wait for them)
    for future in as_completed(responses):
        res = future.result()
        print(f"[{threading.current_thread().name}]Status: {res.status_code}\nResult: {res.text}")


# Main function, run on startup
if __name__ == "__main__":
    # Load the config
    with open("./config.toml") as f:
        config = toml.load(f)
    print("Starting Ground Stations...")
    # Read the list of the gsts
    gstsList = loadGSTsInfo(config)
    # Create GSTs threads
    print(f"Creating {len(gstsList)} threads...\n")
    createGSTs(config, gstsList)
