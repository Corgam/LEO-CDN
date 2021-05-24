####################
##    STARDUST    ##
####################

# importing the requests library
import requests
import json
import http.client

# GET URL
BASE_URL = "http://172.26.8.3:5000"

KEYGROUPS = BASE_URL + "/getKeygroups"
INIT = BASE_URL + "/initializeKeygroup"
ADD_DATA = BASE_URL + "/addData/test/testid"
GETVALUE = BASE_URL + "/getValue/testid"

LOCATION = BASE_URL + "/getLocation"
SETLOCATION = BASE_URL + "/setLocation"
POSITIONS = BASE_URL + "/positions"

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


# Choose the best satelitte to send the HTTP requests to
def connectToTheBestSatellite():
    # TODO: Communicate with the Coordinator to choose the best satellite.
    ip = "172.26.8.3"
    port = "5000"
    return http.client.HTTPConnection(ip,port);


# Send all requests to the best satellite
def sendRequests(reqsList):
    # Create a connection to the best satellite
    conn = connectToTheBestSatellite()
    # Send all requests
    for req in reqsList:
        # Send the request
        conn.request(method="GET",url=req.getURL(),headers=req.getHeads())
        # Get response
        response = conn.getresponse()
        print(f"Status: {response.status} and reason: {response.reason}")


# Main function, run on startup
if __name__ == "__main__":

    # Read all requests from the file
    reqsList = readRequests()
    print(f"Sending all {len(reqsList)} HTTP requests...")
    sendRequests(reqsList)

    # Old functionality, to test press enter
    input("\nPress ENTER to continue and start testing custom HTTP requests")

    # Get all keygroups of node 1
    print('Get all keygroups..')
    r = requests.get(url=KEYGROUPS)

    print(r.text)
    print('-------------------------')

    # Initialize keygroup test
    print('Initialize keygroup..')
    r = requests.post(url=INIT, data='test')
    print(r.text)
    print('-------------------------')

    # Add value
    print('Add data..')
    headers = {'Content-type': 'application/json'}
    data = {
        'testx': '123'
    }
    r = requests.post(url=ADD_DATA, data=json.dumps(data), headers=headers)
    print(r.text)
    print('-------------------------')

    # Get value
    print('Get value..')
    r = requests.get(url=GETVALUE)
    print(r.text)
    print('-------------------------')

    ###################
    ## Position test ##
    ###################

    # Get latest position of node
    print('Get node1 location..')
    r = requests.get(url=LOCATION)

    position = None
    if not r.text.startswith("<!DOCTYPE HTML PUBLIC "):
        print(r.text)
        # Change coordinates
        position = json.loads(r.text.replace("'", '"'))
        position["x"] += 1
        position["y"] += 1
        position["z"] += 1

    else:
        print('error')
        
    print('-------------------------')

    if not position == None:
        # Changes position of node 1
        print('Change position..')
        r = requests.post(url=SETLOCATION, data=json.dumps(position))

        # print response
        print(r.text)
        print('')
        print('-------------------------')

        # Get latest position of node 1
        print('Get all positions..')
        r = requests.get(url=POSITIONS)

        # print response
        print(r.text)
