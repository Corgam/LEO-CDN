######################
##COORDINATOR CLIENT##
######################

# importing the requests library
import requests
import json
#import http.client

satellite_pos = []

# GET URL
BASE_URL = "http://172.26.7.3:5000"

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

def storePositions(r):
    #TODOFind out data type of r and convert it to some satellite_pos dictionary
    satellite_pos = r
    return satellite_pos

def getPositions():
    print('Get all satellites\' position..')
    r = requests.get(url=POSITIONS)

    print(r.text)
    print('-------------------------')

    storePositions(r)

# Main function, run on startup
if __name__ == "__main__":
    pass

    