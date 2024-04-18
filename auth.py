import requests
import datetime
import concurrent.futures
import pandas as pd

from generate_token import generate_signed_jwt
from urllib.parse import urlsplit

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
        return access_token, refresh_token
    else:
        print("Failed to obtain access token")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None, None

def fetch_groups(endCursor=""):
    URL = "https://api.meetup.com/gql"
    access_token, refresh_token = authenticate()

    if not access_token:
        print("Authentication failed, cannot proceed to fetch events.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = {
        "query": """
        query (
            $searchGroupInput: ConnectionInput!, 
            $searchGroupFilter: SearchConnectionFilter!,
            $sortOrder: KeywordSort!
        ) {
            keywordSearch(
                input: $searchGroupInput, 
                filter: $searchGroupFilter,
                sort: $sortOrder
            ) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                edges {
                    node {
                        result {
                            ... on Group {
                                id
                                name
                                urlname
                                latitude
                                longitude
                            }
                        }
                    }
                }
            }
        }
        """,
        "variables": {
            "searchGroupFilter": {
                "query": "Rust",
                "lat": 0.0,
                "lon": 0.0,
                "radius": 20000,
                "source": "GROUPS"
            },
            "searchGroupInput": {
                "first": 200,
                "after": endCursor
            },
            "sortOrder":{
                "sortField": "RELEVANCE"
            }
        }
    }
    return requests.post(url=URL, headers=headers, json=data)

def get_rush_groups():
    """
    Return a dictionary of groups
    """
    endCursor = None
    groups = dict()
    while True:
        data = fetch_groups(endCursor).json()
        edges = data['data']['keywordSearch']['edges']
        pageInfo = data['data']['keywordSearch']['pageInfo']
        for node in edges:
            group = node["node"]["result"]
            if not (group["id"] in groups):
                groups[group["id"]] = group
        if pageInfo['hasNextPage']:
            endCursor = pageInfo['endCursor']
        else:
            break
    return groups

def get_known_rush_groups(fileName):
    """
    Read url and location of groups. Extract the urlname from the url
    Return a dictionary of groups
    """
    groups = dict()
    df = pd.read_csv(fileName, header=0, usecols=['url', 'location'])

    # Format: [source](https://stackoverflow.com/questions/35616434/how-can-i-get-the-base-of-a-url-in-python)
    # https://www.meetup.com/seattle-rust-user-group/
    # split_url.scheme   "http"
    # split_url.netloc   "www.meetup.com" 
    # split_url.path     "/seattle-rust-user-group/"
    for index, row in df.iterrows():
        split_url = urlsplit(row["url"])
        group = {}
        group["urlname"] = (split_url.path).replace("/", "")
        group["location"] = row["location"]
        groups[index] = group
        # print(groups[index])
    return groups

def get_20_events(groups):
    # TODO: Make sure list of 20 events has all values for list of Event
    events = list()
    URL = "https://api.meetup.com/gql"
    access_token, refresh_token = authenticate()

    if not access_token:
        print("Authentication failed, cannot proceed to fetch events.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {}
    count = 1
    for group in groups.values():
        urlName = str(group["urlname"])
        # print(urlName)
        data = {
            "query": """
            query ($urlName: String!, $searchEventInput: ConnectionInput!) {
                groupByUrlname(urlname: $urlName) {
                    upcomingEvents(input: $searchEventInput, sortOrder: ASC) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                        edges {
                            node {
                                id
                                title
                                eventUrl
                                dateTime
                            }
                        }
                    }
                }
            }
            """,
            "variables": {
                "urlName": urlName,
                "searchEventInput": {
                    "first": 20
                }
            }
        }
        response = requests.post(url=URL, headers=headers, json=data)
        data = response.json()["data"]
        if data:
            searchGroupByUrlname = data["groupByUrlname"]
            if searchGroupByUrlname:
                edges = searchGroupByUrlname["upcomingEvents"]["edges"]
                if edges:
                    print(count, urlName, "\n",edges)
                    print()
                    count += 1

def get_events() -> list[Event]:
    # event_list = list()
    groups = get_rush_groups()
    events = get_20_events(groups)
    # event_list = generate_event_list(get_20_events(groups), event_list)
    print("\nNext events\n")
    # groups = get_known_rush_groups("rust_meetup_groups.csv")
    # get_20_events(groups)
    return event_list

# TODO: Generate events into list of Event
# def generate_event_list(events, event_list) -> list[Event]:
    # Event(name, location, date, url, virtual, organizerName, organizerUrl, duplicate=False)
    # event_list.append(Event(name, location, date, url, virtual, organizerName, organizerUrl))
    # return event_list

# print(get_rush_groups())