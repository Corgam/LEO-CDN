#####################
## Ground Stations ##
#####################

import http.client
import json
import math
import threading

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

    # Returns the URL of the HTTP Request
    def getURL(self):
        return self.URL

    # Returns the dict of heads of the HTTP Request
    def getHeads(self):
        return self.heads


# This class holds information about one groundstation
class GST:
    def __init__(self, id, latitude, longitude, country, numberOfRequests):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.country = country
        self.numberOfRequests = numberOfRequests

    # Returns the ID of the GST
    def getID(self):
        return self.id

    # Returns the latitude of the GST
    def getLatitude(self):
        return self.latitude

    # Returns the longitude of the GST
    def getLongitude(self):
        return self.longitude

    # Returns the country of the GST
    def getCountry(self):
        return self.country

    # Returns the numberOfRequests the GST will send
    def getNumberOfRequests(self):
        return self.numberOfRequests


#########################
## Internal functions  ##
#########################

# Load the GSTs info into a list
def loadGSTsInfo():
    gstsList = list()
    # Treat each line as new object
    df_gst = pd.read_csv("/gsts.csv")
    for index, gst in df_gst.iterrows():
        gstsList.append(
            GST(
                gst.id,
                float(gst.lat),
                float(gst.lng),
                gst.country,
                # TODO: make number of requests (per second?) depend on population
                10,
            )
        )
    return gstsList


# Create all threads and all GSTs
def createGSTs(gstsList):
    # Load the config
    with open("./config.toml") as f:
        config = toml.load(f)
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
        threads.append(threading.Thread(target=sendRequests, args=(gstList,)))
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
    return reqsList


# Choose the best satelitte to send the HTTP requests to, by communicating with the coordinator
def getTheBestSatellite(id):
    # Communicate with the Coordinator to choose the best satellite.
    coordConn = http.client.HTTPConnection("172.26.4.1", "9001")
    coordConn.request(method="GET", url=f"/best_satellite/{id}")
    # Get the response
    res = coordConn.getresponse()
    # Extract ip and port
    data = res.read().decode()
    if data != "Invalid GST ID":
        # Return the ip and port to the best satellite
        print(
            f"[{threading.current_thread().name}]Answer from coordinator received: {data}.\n"
        )
        coordConn.close()
        return data
    else:
        return -1


# Send all requests to the best satellite
def sendRequests(gstList):
    responses = []
    for gst in gstList:
        # Generate the requests
        reqsList = generateRequests(gst.getID(), 0.1, gst.getNumberOfRequests())
        # Create a connection to the best satellite
        print(
            f"[{threading.current_thread().name}]Sending query to coordinator for the best satellite...\n"
        )
        bestSat = getTheBestSatellite(gst.getID())
        if bestSat == -1:
            print(f"[{threading.current_thread().name}]Invalid GST ID...\n")
            return
        # Send all requests
        print(
            f"[{threading.current_thread().name}]Sending all {len(reqsList)} HTTP requests...\n"
        )
        # Create an async session
        session = FuturesSession()
        for req in reqsList:
            # Send the request in an async fashion
            responses.append(session.get("http://" + bestSat + req.getURL()))
    # Read all of the responses (wait for them)
    for future in responses:
        res = future.result()
        print(f"[{threading.current_thread().name}]Status: {res.status_code}\n")


# Main function, run on startup
if __name__ == "__main__":
    print("Starting Ground Stations...")
    # Read the list of the gsts
    gstsList = loadGSTsInfo()
    # Create GSTs threads
    print(f"Creating {len(gstsList)} threads...\n")
    createGSTs(gstsList)
