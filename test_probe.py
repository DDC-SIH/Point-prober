import requests
import json

# Endpoint URL
url = "http://127.0.0.1:5000/probe"

# Test data for a single date
test_data = {
    "lon": 103.8198,  # Example longitude (Singapore)
    "lat": 1.3521,    # Example latitude (Singapore)
    "bands": [1, 2, 3],  # Request only the first 3 bands
    "date": "2025-03-22"  # Date matching the sample file
}

# Send the POST request
response = requests.post(url, json=test_data)

# Print the response
print("Status Code:", response.status_code)
print("Response:")
print(json.dumps(response.json(), indent=2)) 