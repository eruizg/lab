import requests
import base64

organization = "PakEnergy"
project = "Accounting"
#run_id = "119612"
result_id = "100002"
pat = ""

# url = f"https://dev.azure.com/{organization}/{project}/_apis/test/Runs/{run_id}/results?api-version=7.1-preview.6"
headers = {
     'Content-Type': 'application/json',
     'Authorization': 'Basic ' + base64.b64encode((':'.join(['', pat])).encode()).decode()
 }
# data = [
#   {
#     "id": 123,
#     "state": "Completed",
#     "comment": "this was changed using Automation",
#     "outcome": "Failed",
#     "testCase": {
#         "id": 1099
#     }
    
    
#   }
 
# ]

# response = requests.patch(url, json=data, headers=headers)
# print(response.status_code)
# print(response.json())

run_id = 119670 # Replace with the run ID from the previous response
url = f"https://dev.azure.com/{organization}/{project}/_apis/test/runs/{run_id}/results?api-version=7.1-preview.3"
data = [
    {
        "testCase": {
            "id": 6650
        },
       
    },
   
]

response = requests.post(url, json=data, headers=headers)
print(response.status_code)
print(response.json())