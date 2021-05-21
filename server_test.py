# importing the requests library
import requests
import json

# GET URL
BASE_URL = "http://172.26.8.3:5000"

KEYGROUPS = BASE_URL + "/getKeygroups"
INIT = BASE_URL + "/initializeKeygroup"
ADD_DATA = BASE_URL + "/addData/test/testid"
GETVALUE = BASE_URL + "/getValue/testid"

LOCATION = BASE_URL + "/getLocation"
SETLOCATION = BASE_URL + "/setLocation"
POSITIONS = BASE_URL + "/positions"

####################
## Keygroup tests ##
####################

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

# Add data
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
