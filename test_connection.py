import requests

try:
    response = requests.get('http://localhost:8081', timeout=5)
    print(f"Status code: {response.status_code}")
    print("Response content:")
    print(response.text[:500])  # Print first 500 chars of response
except Exception as e:
    print(f"Error connecting to server: {str(e)}")
