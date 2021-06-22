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

    # r = requests.get(url=LOCATION)
    # print(r.text)
    # print('-------------------------')

    # r = requests.get(url=KEYGROUP)
    # print(r.text)
    # print('-------------------------')

    # r = requests.get(url=KEYGROUPS)
    # print(r.text)
    # print('-------------------------')

    # r = requests.get(url=ADDRESSES)
    # print(r.text)
    # print('-------------------------')

    headers = {'host': 'http://riptutorial.com'}
    print('Get https://riptutorial.com/flask/example/19420/catch-all-route..')
    r = requests.get(url=TESTURL, headers=headers)
    print(r.text)
    print('-------------------------')

    print('Get https://riptutorial.com/flask/example/19420/catch-all-route..')
    r = requests.get(url=TESTURL, headers=headers)
    print(r.text)
    print('-------------------------')