import requests
from datetime import datetime, timedelta
import sys
import json
from colorama import Fore, Style
from tabulate import tabulate

def query_blackholed_date(username, token):
    url = f"https://api.intra.42.fr/v2/users/{username}/cursus_users"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        cursus_users = response.json()
        for cursus_user in cursus_users:
            blackholed_at = cursus_user.get('blackholed_at')
            if blackholed_at and blackholed_at != 'null':
                return blackholed_at
        print("No blackholed date found.")
        return None
    else:
        print(f"Error fetching cursus users data: {response.status_code}, {response.text}")
        return None

def query_projects(username, token):
    url = f"https://api.intra.42.fr/v2/users/{username}/projects_users"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching projects data: {response.status_code}, {response.text}")
        return []

def get_most_recent_validation(projects):
    """Extract the most recent validation date from validated projects."""
    validated_projects = []
    for project in projects:
        # Assuming validation can be inferred from 'final_mark' and 'status'
        if project.get('final_mark') is not None and project.get('status') == 'finished':
            for team in project.get('teams', []):
                # Assuming the 'updated_at' field in teams can serve as a proxy for validation date
                if team.get('final_mark') is not None:
                    validated_projects.append(team)

    if validated_projects:
        # Use 'updated_at' as a proxy for the validation date
        latest_project = max(validated_projects, key=lambda p: datetime.fromisoformat(p['updated_at'].rstrip('Z')))
        return datetime.fromisoformat(latest_project['updated_at'].rstrip('Z'))
    return None

def calculate_validation_time(last_validation_date):
    """Calculate days since last validation and days before hitting the blackhole."""
    if last_validation_date:
        today = datetime.now()
        days_since_last_validation = (today - last_validation_date).days
        return days_since_last_validation
    return None

def get_current_chunk_dates():
    base_start_date = datetime(2024, 5, 17)
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
        print("Usage: python script.py <login>")
        sys.exit(1)
    
    token = generate_token()
    if not token:
        print("Failed to generate token. Please check your credentials.")
        sys.exit(1)

    username = sys.argv[1]
    start_at, end_at = get_current_chunk_dates()
    locations = query_user_hours(username, start_at, end_at, token)
    
    total_hours = calculate_total_hours(locations)
    total_hours_formatted = f"{Style.BRIGHT}{total_hours:.2f}{Style.RESET_ALL}"
    print(f"{Fore.BLUE}User {username} spent a total of {total_hours_formatted} {Fore.BLUE}hours from {start_at} to {end_at}.{Style.RESET_ALL}")

    projects = query_projects(username, token)
    last_validation_date = get_most_recent_validation(projects)
    days_since_last_validation = calculate_validation_time(last_validation_date)

    if last_validation_date:
        print(f"{Fore.GREEN}Last project validated on: {Fore.WHITE}{last_validation_date.strftime('%Y-%m-%d')}")
        print(f"{Fore.GREEN}Days since last project validation: {Fore.WHITE}{days_since_last_validation}{Style.RESET_ALL}")
        blackholed_date_str = query_blackholed_date(username, token)
        if blackholed_date_str:
            blackholed_date = datetime.fromisoformat(blackholed_date_str.rstrip('Z'))
            days_until_blackhole = (blackholed_date - datetime.now()).days
            print(f"{Fore.RED}Blackhole date: {Fore.WHITE}{blackholed_date.strftime('%Y-%m-%d')}")
            print(f"{Fore.RED}Days until blackhole: {Fore.WHITE}{days_until_blackhole}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Failed to fetch blackhole date.{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No validated projects found or unable to calculate.{Style.RESET_ALL}")
