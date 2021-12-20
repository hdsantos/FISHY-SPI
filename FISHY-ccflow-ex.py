#CCF example Python  

import requests  

#URL receives the endpoint 
token_service_url = 'http://localhost:8080/auth/realms/test/protocol/openid-connect/token' 

credential = { #Parameters for the call 
                'client_id': 'python_fishy',   
                'client_secret': '747ab86d-97f0-4f10-8a2e-dccccb176756', 
                'scope':'email',  
                'grant_type':'client_credentials'  
             }  

#Test errors!  
request = requests.post(token_service_url, data = credential)
#prints the Access Token – JWS 
print(request.text) 

#--get data from server using token 'request'
#--process data
#--repeat until required
