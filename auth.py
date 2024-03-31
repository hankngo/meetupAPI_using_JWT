import requests
import datetime
import concurrent.futures

from generate_token import generate_signed_jwt

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

print(len(get_rush_groups()))

def get_events(groups):
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
    for group in groups:
        urlName = group["urlName"]
        data = {
            "query": """
            query (
                $searchEventInput: EventAdminInput!, 
                $searchEventsFilter: GroupEventsFilter!,
                $sortOrder: SortOrder!
            ) {
                groupByUrlname(input: f{urlName}) {
                    unifiedEvents(
                        input: $searchEventInput
                        filter: $searchEventsFilter
                        sortOrder: $sortOrder
                    ) {
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
                "searchEventsFilter": {
                    "query": "Rust",
                    "lat": 0.0,
                    "lon": 0.0,
                    "source": "GROUPS",
                    "startTime": datetime.datetime.now(),
                    "endTime": ""
                },
                "searchEventInput": {
                    "first": 200,
                    "after": endCursor
                },
                "sortOrder":{
                    "sortField": "RELEVANCE"
                }
            }
        }
    pass