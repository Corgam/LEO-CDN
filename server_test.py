# importing the requests library
import requests
  
# GET URL
GET_URL = "http://172.26.8.3:5000/getKeygroups"  
POST_URL = "http://172.26.8.3:5000/test/addKeygroup"  
  
# sending get request and saving the response as response object
r = requests.get(url = GET_URL)
  
# print response
print(r.text)
print('-------------------------')

# sending a post request and saving the response as reponse object
r = requests.post(url = POST_URL, data = 'test')

#print response
print(r.text)
print('')
print('-------------------------')

# sending get request and saving the response as response object
r = requests.get(url = GET_URL)
  
# print response
print(r.text)