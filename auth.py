import requests
import datetime

from generate_token import generate_signed_jwt

# WEDNESDAY_DATETIME_DAY = 2
# END_DATE_WEEKS = 4 # Number of weeks to skip
# def get_closest_wednesday():
#     """
#     Returns the closest Wednesday to the current day
#     """
#     day = datetime.datetime.today()

#     while day.weekday() != WEDNESDAY_DATETIME_DAY:
#         day += datetime.timedelta(days=1)
    
#     return day

# def get_desired_date_range():
#     """
#     Returns datetime.datetime for the next closest Wednesday, and the Wednesday that 
#     is four weeks later.
#     """
#     closest_wednesday = get_closest_wednesday()

#     # We add END_DATE_WEEKS, and 1 day because Meetup requires DAY+1 for proper querying
#     end_date = closest_wednesday + datetime.timedelta(weeks=END_DATE_WEEKS, days=1) 

#     return closest_wednesday, end_date

def authenticate():
    URL = "https://secure.meetup.com/oauth2/access"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": generate_signed_jwt()
    }
    response = requests.post(url=URL, headers=headers, data=body)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        refresh_token = response.json().get("refresh_token")
        print("Access Token:", access_token, "\nRefresh token: ", refresh_token)
        return access_token, refresh_token
    else:
        print("Failed to obtain access token")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None, None

def get_events():
    URL = "https://api.meetup.com/gql"
    access_token, refresh_token = authenticate()
    if not access_token:
        print("Authentication failed, cannot proceed to fetch events.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    # timeMin, timeMax = get_desired_date_range()
    # print("Start Date: ", timeMin.isoformat(), "\tEnd Date: ", timeMax.isoformat())
    data = {
        "query": """
        query SearchEvents($searchFilter: SearchConnectionFilter!) {
            keywordSearch(filter: $searchFilter) {
                edges {
                    node {
                        result {
                            ... on Event {
                                title
                                eventUrl
                                dateTime
                                isOnline
                                venues {
                                    name
                                    address
                                    city
                                    state
                                    country
                                    postalCode
                                    venueType
                                    lat
                                    lon
                                }
                                shortDescription
                            }
                        }
                    }
                }
            }
        }
        """,
        "variables": {
            "searchFilter": {
                "query": ".*",
                "lat": 0.0,
                "lon": 0.0,
                "radius": 20000,
                "source": "EVENTS"
            }
        }
    }
    response = requests.post(url=URL, headers=headers, json=data)
    print(response.json())

get_events()