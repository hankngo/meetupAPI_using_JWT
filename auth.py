import requests
from generate_token import generate_signed_jwt

URL = "https://secure.meetup.com/oauth2/access"
CONTENT_TYPE = "application/x-www-form-urlencoded"
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"

def authenticate():
    headers = {"Content-Type": CONTENT_TYPE}
    body = {
        "grant_type": GRANT_TYPE,
        "assertion": generate_signed_jwt()
    }
    response = requests.post(url=URL, headers=headers, data=body)
    # Checking the response
    if response.status_code == 200:
        # If the request was successful, get the access_token, and refresh_token
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        print("Access Token:", access_token, "\nRefresh token: ", refresh_token)
    else:
        print("Failed to obtain access token")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

authenticate()