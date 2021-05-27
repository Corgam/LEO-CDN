####################
##    STARDUST    ##
####################

# importing the requests library
import requests
import json
import http.client

# GET URL
BASE_URL = "http://172.26.9.3:5000"

KEYGROUPS = BASE_URL + "/getKeygroups"
INIT = BASE_URL + "/initializeKeygroup"
ADD_DATA = BASE_URL + "/setData/test2/testid"
ADD_MANAGE = BASE_URL + "/addToKeygroup"
ADD_MANAGE2 = BASE_URL + "/addKeygroup"
GETVALUE = BASE_URL + "/getValue/manage/addresses"
GETVALUE2 = BASE_URL + "/getValue/manage/positions"

LOCATION = BASE_URL + "/getLocation"
SETLOCATION = BASE_URL + "/setLocation"
POSITIONS = BASE_URL + "/positions"
ADD_ROLE = BASE_URL + "/addRoles/manage"
ADD_ROLE2 = BASE_URL + "/addRole/manage"
APPEND = BASE_URL + "/appendData/manage/addresses"


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
                reqsList.append(req)
                req = ""                
            else:
                req = req + line;
        # Add the last request after EOF
        reqsList.append(req)
        return reqsList

# Send all requests 
def sendRequests(reqsList, ip, port):
    # Create a connection
    conn = http.client.HTTPConnection(ip,port)
    # Send all requests
    for req in reqsList:
        lines = str(req).split('\n')
        # Prepare url
        url = lines[0]
        url = url.replace("GET ","")
        url = url.replace(" HTTP/1.1","")
        # Prepeare headers
        head = {}
        for line in lines:
            if line == lines[0] or line == "":
                continue
            else:
                # Fill in the headers
                parts = line.split(": ")
                head[parts[0]] = parts[1]
        # Send the request
        conn.request(method="GET",url=url,headers=head)
        # Get response
        response = conn.getresponse()
        print(f"Status: {response.status} and reason: {response.reason}")

# Main function, run on startup
if __name__ == "__main__":

    # # Read all requests from the file
    # reqsList = readRequests()
    # print("Sending all HTTP requests...")
    # sendRequests(reqsList,"172.26.8.3","5000")

    # # Old functionality, to test press enter
    # input("\nPress ENTER to continue and start testing custom HTTP requests")

    # # Get all keygroups of node 1
    # print('Get all keygroups..')
    # r = requests.get(url=KEYGROUPS)

    # print(r.text)
    # print('-------------------------')

    # # Initialize keygroup test
    # print('Initialize keygroup..')
    # r = requests.post(url=INIT, data='test2')
    # print(r.text)
    # print('-------------------------')

    # # Add value
    # print('Add data..')
    # headers = {'Content-type': 'application/json'}
    # data = {
    #     'testx': '123'
    # }
    # r = requests.post(url=ADD_DATA, data=json.dumps(data), headers=headers)
    # print(r.text)
    # print('-------------------------')

    # print('joining manage')
    # data = {
    #             'satellite': "satellite1",
    #             'keygroup': "manage",
    #             'fred' : "fred1"
    #         }
    # r = requests.post(url=ADD_MANAGE, data=json.dumps(data))
    # print(r.text)
    # print('-------------------------')

    # data = {
    #             'satellite': "satellite1",
    #             'keygroup': "manage",
    #             'fred' : "fred1"
    #         }
    # r = requests.post(url=ADD_MANAGE2, data=json.dumps(data))
    # print(r.text)
    # print('-------------------------')

    # print('Set role')
    # data = {
    #             'node': "fred",
    #             'level': 1
    #         }
    # r = requests.post(url=ADD_ROLE2, data=json.dumps(data))
    # print(r.text)


    # data = "http://172.26.8.3:5000/"
    # r = requests.post(url=APPEND, data=data)
    # print(r.text)
    # print('-------------------------')
    # Get value
    print('Get value..')
    r = requests.get(url=GETVALUE)
    print(r.text)
    print('-------------------------')
    r = requests.get(url=GETVALUE2)
    print(r.text)
    print('-------------------------')

    

    ##################
    # Position test ##
    ##################

    # # Get latest position of node
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
