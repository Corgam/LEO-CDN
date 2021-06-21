####################
##    STARDUST    ##
####################

# Importing needed libraries
import numpy
import http.client
import threading
from requests_futures.sessions import FuturesSession


# This class holds all the information about a single HTTP Request.
class HTTPRequest:
    def __init__(self, URL, heads):
        self.URL = URL
        self.heads = heads

    # Sets the URL and heads dic from given string. No error check.
    @classmethod
    def fromString(self, reqString):
        lines = str(reqString).split('\n')
        # Prepare url
        url = lines[0]
        url = url.replace("GET ","")
        url = url.replace(" HTTP/1.1","")
        # Prepeare headers
        heads = {}
        for line in lines:
            if line == lines[0] or line == "":
                continue
            else:
                # Fill in the headers
                parts = line.split(": ")
                heads[parts[0]] = parts[1]
        return HTTPRequest(url,heads)

    #Returns the URL of the HTTP Request
    def getURL(self):
        return self.URL
    
    #Returns the dict of heads of the HTTP Request
    def getHeads(self):
        return self.heads

# This class holds information about one groundstation
class Stardust:
    def __init__(self, id, latitude, longitude, country, numberOfRequests):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.country = country
        self.numberOfRequests = numberOfRequests
    # Returns the ID of the stardust
    def getID(self):
        return self.id
    # Returns the latitude of the stardust
    def getLatitude(self):
        return self.latitude
    # Returns the longitude of the stardust
    def getLongitude(self):
        return self.longitude
    # Returns the country of the stardust
    def getCountry(self):
        return self.country
    # Returns the numberOfRequests the stardust will send
    def getNumberOfRequests(self):
        return self.numberOfRequests

#########################
## Internal functions  ##
#########################

# Load the stardusts info into a list
def loadStardustsInfo():
    stardustsList = list()
    # Treat each line as new object
    with open("./stardusts.txt") as f:
        for line in f:
            line = line.replace("\n","")
            id, latitude, longitude, country, numberOfRequests = line.split('|')
            stardustsList.append(Stardust(id, float(latitude), float(longitude), country, int(numberOfRequests)))
    return stardustsList

# Creates a new thread for each stardust
def createStardusts(stardustsList):
    threads = list()
    # Create threads
    for stardust in stardustsList:
        threads.append(threading.Thread(target=sendRequests, args=(stardust,)))
    # Start threads
    for thread in threads:
        thread.start()


# Generates the requests instead of reading them from a file
def generateRequests(numberOfRequests):
    reqsList = list()
    # Create the random geometric distribution
    dis = numpy.random.geometric(0.01,numberOfRequests)
    # Generate the requests 
    for i in range(0, numberOfRequests):
        number = dis[i]
        req = f"GET /file{number} HTTP/1.1"
        reqsList.append(HTTPRequest.fromString(req))
    return reqsList

# Choose the best satelitte to send the HTTP requests to, by communicating with the coordinator
def getTheBestSatellite(id):
    # Communicate with the Coordinator to choose the best satellite.
    coordConn = http.client.HTTPConnection("172.26.4.1", "9001")
    coordConn.request(method="GET",url=f"/best_satellite/{id}")
    # Get the response
    res = coordConn.getresponse()
    # Extract ip and port
    data = res.read().decode()
    if(data != "Invalid GST ID"):
        # Return the ip and port to the best satellite
        print(f"[{threading.current_thread().name}]Answer from coordinator received: {data}.\n")
        coordConn.close()
        return data;
    else:
        return -1; 


# Send all requests to the best satellite
def sendRequests(stardust):
    # Generate the requests
    reqsList = generateRequests(stardust.getNumberOfRequests())
    # Create a connection to the best satellite
    print(f"[{threading.current_thread().name}]Sending query to coordinator for the best satellite...\n")
    bestSat = getTheBestSatellite(stardust.getID())
    if(bestSat == -1):
        print(f"[{threading.current_thread().name}]Invalid Stardust ID...\n")
        return
    # Send all requests
    print(f"[{threading.current_thread().name}]Sending all {len(reqsList)} HTTP requests...\n")
    # Create an async session
    session = FuturesSession()
    responses = list()
    for req in reqsList:
        # Send the request in an async fashion
        responses.append(session.get("http://"+bestSat+req.getURL()))
    # Read all of the responses (or wait for them)
    for future in responses:
        res = future.result()
        print(f"[{threading.current_thread().name}]Status: {res.status_code}\n")

# Main function, run on startup
if __name__ == "__main__":
    print("Starting STARDUST...")
    # Read the list of the stardusts
    stardustsList = loadStardustsInfo()
    # Create stardusts threads
    print(f"Creating {len(stardustsList)} threads...\n")
    createStardusts(stardustsList)

