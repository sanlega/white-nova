import requests
from datetime import datetime, timedelta
import sys
import json

def get_current_chunk_dates():
    base_start_date = datetime(2024, 1, 26)
    today = datetime.now()
    days_since_base = (today - base_start_date).days
    chunk_length = 15

    chunks_since_base = days_since_base // chunk_length
    current_chunk_start_date = base_start_date + timedelta(days=chunks_since_base * chunk_length)
    current_chunk_end_date = current_chunk_start_date + timedelta(days=chunk_length)

    return current_chunk_start_date.strftime('%Y-%m-%dT08:00'), current_chunk_end_date.strftime('%Y-%m-%dT08:00')

def generate_token():
    with open('tokens.json', 'r') as file:
        tokens = json.load(file)

    client_id = tokens['client_id']
    client_secret = tokens['client_secret']
    url = 'https://api.intra.42.fr/oauth/token'

    data = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    response = requests.post(url, data=data)

    if response.status_code == 200:
        token = response.json()['access_token']
        with open('token', 'w') as file:
            file.write(token)
        return token
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None

def query_user_hours(username, start_at, end_at, token):
    base_url = "https://api.intra.42.fr/v2/users/{}/locations?range[end_at]={},{}"
    formatted_url = base_url.format(username, start_at, end_at)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(formatted_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def calculate_total_hours(locations):
    total_seconds = 0
    for location in locations:
        begin_at = datetime.fromisoformat(location['begin_at'].rstrip('Z'))
        end_at = datetime.fromisoformat(location['end_at'].rstrip('Z'))
        duration = end_at - begin_at
        total_seconds += duration.total_seconds()

    return total_seconds / 3600

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <username>")
        sys.exit(1)
    
    token = generate_token()
    if not token:
        print("Failed to generate token. Please check your credentials.")
        sys.exit(1)

    username = sys.argv[1]
    start_at, end_at = get_current_chunk_dates()
    locations = query_user_hours(username, start_at, end_at, token)
    
    total_hours = calculate_total_hours(locations)
    print(f"User {username} spent a total of {total_hours:.2f} hours from {start_at} to {end_at}.")
