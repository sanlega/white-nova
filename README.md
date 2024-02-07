# 42 API User Hours Query Script

This Python script queries the 42 API to determine the number of hours a specified user has spent on campus within dynamically calculated 15-day chunks. The calculation begins from January 26, 2024, and automatically adjusts to cover the next 15-day period as time progresses.

## Getting Started

Before you use the script, ensure you have Python installed on your system and have obtained your 42 API credentials (client ID and client secret).

### Prerequisites

- Python 3.x
- `requests` library installed in your Python environment. You can install this library using pip:

```bash
pip install requests
```

### Configuration

1. **Obtain 42 API Credentials**: You must first register your application with the 42 API to obtain your client ID and client secret.

2. **Setup `tokens.json` File**: Create a `tokens.json` file in the same directory as the script with your 42 API credentials as follows:

```json
{
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
}
```

Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with the credentials provided by the 42 API.

### Usage

To run the script, use the following command in your terminal, replacing `<login>` with the 42 login of the user you want to query:

```bash
python script.py <login>
```

This will output the total number of hours the specified user spent on campus in the current 15-day chunk.
