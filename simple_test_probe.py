import requests
import json
import subprocess
import os

print("This script demonstrates two ways to test the probe endpoint")

# Method 1: Using requests library
def test_with_requests():
    print("\n=== Testing with requests library ===")
    url = "http://127.0.0.1:5000/probe"
    
    # Test data for a single date
    test_data = {
        "lon": 103.8198,
        "lat": 1.3521,
        "bands": [1, 2, 3],
        "date": "2025-03-22"
    }
    
    print(f"Sending POST request to {url} with data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

# Method 2: Using curl command
def test_with_curl():
    print("\n=== Testing with curl command ===")
    curl_cmd = 'curl -X POST -H "Content-Type: application/json" -d "{\\"lon\\": 103.8198, \\"lat\\": 1.3521, \\"bands\\": [1, 2, 3], \\"date\\": \\"2025-03-22\\"}" http://127.0.0.1:5000/probe'
    
    print(f"Running command:\n{curl_cmd}")
    try:
        result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
        print("\nResponse:")
        try:
            formatted_json = json.dumps(json.loads(result.stdout), indent=2)
            print(formatted_json)
        except:
            print(result.stdout)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_with_requests()
    test_with_curl() 