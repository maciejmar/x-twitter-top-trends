import tweepy
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

# Replace these values with your actual credentials
api_key = os.getenv('API_KEY')
api_secret_key = os.getenv('API_SECRET_KEY')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
print('api_key=',api_key)

# Authenticate to X
auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)

# Create an API object
api = tweepy.API(auth)

# WOEID for worldwide
worldwide_woeid = 1

# Fetch trending topics
trends = api.get_place_trends(worldwide_woeid)

# Extract and print the top 10 trends
for trend in trends[0]['trends'][:10]:
    print(trend['name'])
    
# Fetch available trend locations
available_locs = api.trends_available()

# Find WOEID for Warsaw
warsaw_woeid = None
for loc in available_locs:
    if loc['name'].lower() == 'warsaw':
        warsaw_woeid = loc['woeid']
        break

if warsaw_woeid:
    # Fetch trending topics for Warsaw
    trends = api.get_place_trends(warsaw_woeid)
    for trend in trends[0]['trends'][:10]:
        print(trend['name'])
else:
    print("WOEID for Warsaw not found.")
