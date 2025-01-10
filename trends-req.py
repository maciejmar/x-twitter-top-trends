import base64
from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Replace these values with your actual credentials
api_key = os.getenv('API_KEY')
api_secret_key = os.getenv('API_SECRET_KEY')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
print('api_key=',api_key)

print('api_secret_key=',api_secret_key)

# Encode consumer key and secret
credentials = f"{api_key}:{api_secret_key}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

print(f"Encoded Credentials: {encoded_credentials}")


# Replace with your encoded credentials
#encoded_credentials = "YOUR_ENCODED_CREDENTIALS"

url = "https://api.x.com/oauth2/token"
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
}
data = {"grant_type": "client_credentials"}

response = requests.post(url, headers=headers, data=data)

if response.status_code == 200:
    bearer_token = response.json()["access_token"]
    print(f"Bearer Token: {bearer_token}")
else:
    print(f"Failed to obtain bearer token: {response.status_code} - {response.text}")
    
    
# Replace with your Bearer Token
#bearer_token = bearer_token

# WOEID for United States
us_woeid = 23424977
url = f"https://api.x.com/2/trends/by/woeid/{us_woeid}"

headers = {
    "Authorization": f"Bearer {bearer_token}"
}

#response = requests.get(url, headers=headers)

# if response.status_code == 200:
#     trends = response.json()["data"]
#     print("Top Trends in the US:")
#     for trend in trends:
#         print(f"Name: {trend['trend_name']}, Tweets: {trend.get('tweet_count', 'N/A')}")
# else:
#     print(f"Failed to fetch trends: {response.status_code} - {response.text}")
    
    
#bearer_token = "YOUR_BEARER_TOKEN"
print ('this is bearer_token - ', bearer_token)
# Set the WOEID (e.g., 23424977 for US)
woeid = 23424977

# Request trends by WOEID
url = f"https://api.x.com/2/trends/by/woeid/{woeid}"
headers = {
    "Authorization": f"Bearer {bearer_token}",
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    trends = response.json()["data"]
    print("Trends:")
    for trend in trends:
        print(f"Trend: {trend['trend_name']}, Tweet Count: {trend.get('tweet_count', 'N/A')}")
else:
    print(f"Failed to fetch trends: {response.status_code} - {response.text}")
    

