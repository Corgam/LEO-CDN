####################
##    STARDUST    ##
####################

# importing the requests library
import requests
import json
import http.client

# Global variables
GST_ID = "gst-0"

# GET URLs
#["http://172.26.9.3:5000/", "http://172.26.8.3:5000/", "http://172.26.7.3:5000/"]
BASE_URL = "http://172.26.8.3:5000"
#(6921000.0, 0.0, 0.0)
#(6921000.0, 0.0, 0.0)

KEYGROUP = BASE_URL + "/currentKeygroup"
LOCATION = BASE_URL + "/getLocation"
KEYGROUPS = BASE_URL + "/getKeygroups"
ADDRESSES = BASE_URL + "/getAddresses"

TESTURL = BASE_URL + "/flask/example/19420/catch-all-route"

class HTTPRequest:
    """
    This class holds all the information about a single HTTP Request.
    Parameters
    ----------
    URL: str
    heads: dict
    """
    def __init__(self, URL, heads):
        self.URL = URL
        self.heads = heads

    @classmethod
    def fromString(self, reqString):
        """
        Sets the URL and heads dic from given string.
        There is no error check.
        Parameters
        ----------
        reqString : string
            string containing url and heads
        Returns
        -------
        """
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

    def getURL(self):
        """
        Returns the URL of the HTTP Request
        Returns
        -------
        URL: string
        """
        return self.URL

    def getHeads(self):
        """
        Returns the dict of heads of the HTTP Request
        Returns
        -------
        heads: dic
        """
        return self.heads

#########################
## Internal functions  ##
#########################


# Read the requests from the txt file and save them in array
def readRequests():
    reqsList = list()
    req = ""
    # Open the requests file and read lines
    with open("./requests.txt","r") as f:
        for line in f:
            # If empty line is encountered
            if line == "\n":
                #Create an string 
                reqsList.append(HTTPRequest.fromString(req))
                req = ""                
            else:
                req = req + line;
        # Add the last request after EOF
        reqsList.append(HTTPRequest.fromString(req))
        return reqsList


# Choose the best satelitte to send the HTTP requests to, by communicating with the coordinator
def connectToTheBestSatellite():
    # Communicate with the Coordinator to choose the best satellite.
    coordConn = http.client.HTTPConnection("172.26.5.1","9001")
    coordConn.request(method="GET",url=f"/best_satellite/{GST_ID}")
    # Get the response
    res = coordConn.getresponse()
    # Extract ip and port
    data = res.read().decode()
    ip,port = data.split(':')
    # Return connection to the best satellite
    print(f"Answer from coordinator received: {data}.")
    return http.client.HTTPConnection(ip,port);


# Send all requests to the best satellite
def sendRequests(reqsList):
    # Create a connection to the best satellite
    print("Sending query to coordinator for the best satellite...")
    conn = connectToTheBestSatellite()
    # Send all requests
    print(f"Sending all {len(reqsList)} HTTP requests...")
    for req in reqsList:
        # For now do not send the real request. The satellite server will not respond right now.
        print(f"Fake News: Sending HTTP request with URL: {req.getURL()}")

        # Send the request
        #conn.request(method="GET",url=req.getURL(),headers=req.getHeads())
        # Get response
        #response = conn.getresponse()
        #print(f"Status: {response.status} and reason: {response.reason}")


# Main function, run on startup
if __name__ == "__main__":

    ###################
    ## Position test ##
    ###################

    # Get latest position of node
    # print('Get node1 location..')
    # r = requests.get(url=LOCATION)

    # position = None
    # if not r.text.startswith("<!DOCTYPE HTML PUBLIC "):
    #     print(r.text)
    #     # Change coordinates
    #     position = json.loads(r.text.replace("'", '"'))
    #     position["x"] += 1
    #     position["y"] += 1
    #     position["z"] += 1

    # else:
    #     print('error')
        
    # print('-------------------------')

    # if not position == None:
    #     # Changes position of node 1
    #     print('Change position..')
    #     r = requests.post(url=SETLOCATION, data=json.dumps(position))

    #     # print response
    #     print(r.text)
    #     print('')
    #     print('-------------------------')

    #     # Get latest position of node 1
    #     print('Get all positions..')
    #     r = requests.get(url=POSITIONS)

    #     # print response
    #     print(r.text)

    ###################
    ##  Random test  ##
    ###################

    r = requests.get(url=LOCATION)
    print(r.text)
    print('-------------------------')

    r = requests.get(url=KEYGROUP)
    print(r.text)
    print('-------------------------')

    # r = requests.get(url=KEYGROUPS)
    # print(r.text)
    # print('-------------------------')

    # r = requests.get(url=ADDRESSES)
    # print(r.text)
    # print('-------------------------')

    

    # headers = {'host': 'http://riptutorial.com'}
    # print('Get https://riptutorial.com/flask/example/19420/catch-all-route..')
    # r = requests.get(url=TESTURL, headers=headers)
    # print(r.text)
    # print('-------------------------')

    # print('Get https://riptutorial.com/flask/example/19420/catch-all-route..')
    # r = requests.get(url=TESTURL, headers=headers)
    # print(r.text)
    # print('-------------------------')