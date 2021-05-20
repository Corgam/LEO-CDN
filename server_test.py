# importing the requests library
import requests
import json
  
# GET URL
KEYGROUPS = "http://172.26.8.3:5000/getKeygroups"  
INIT = "http://172.26.8.3:5000/initializeKeygroup"    
GETVALUE = "http://172.26.8.3:5000/getValue/testid"  

LOCATION = "http://172.26.8.3:5000/getLocation"  
SETLOCATION = "http://172.26.8.3:5000/setLocation"
  
####################
## Keygroup tests ##
####################

# Get all keygroups of node 1
print('Get all keygroups..')
r = requests.get(url = KEYGROUPS)

print(r.text)
print('-------------------------')

# Initialize keygroup test
print('Initialize keygroup..')
r = requests.post(url = INIT, data = 'test')
print(r.text)
print('-------------------------')

# Get value
print('Get value..')
r = requests.get(url = GETVALUE)
print(r.text)
print('-------------------------')

###################
## Position test ##
###################

# Get latest position of node 1
print('Get node1 location..')
r = requests.get(url = LOCATION)
  
print(r.text)
print('-------------------------')

# Change coordinates
position = json.loads(r.text)
position["x"] += 1
position["y"] += 1
position["z"] += 1

# Changes position of node 1
print('Change position..')
r = requests.post(url = SETLOCATION, data = json.dumps(position))

#print response
print(r.text)
print('')
print('-------------------------')

# Get latest position of node 1
print('Get latest position..')
r = requests.get(url = LOCATION)
  
# print response
print(r.text)