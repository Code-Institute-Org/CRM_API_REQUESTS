import requests
import json
from tutor_ids import TUTOR_CONTACT_IDS
from ids import *

CLIENT_ID = X
CLIENT_SECRET = X
REFRESH_TOKEN = X
REFRESH_ENDPOINT = "https://accounts.zoho.com/oauth/v2/token"
STUDENTS_ENDPOINT = "https://www.zohoapis.com/crm/v2/contacts"
ACTIVITIES_ENDPOINT = "https://www.zohoapis.com/crm/v2/tasks"
USERS_ENDPOINT = "https://www.zohoapis.com/crm/v2/users"
MAX_PER_PAGE = 200
DATES = {
    'Stalling on submitting a project': "2019-06-04",
    'Not studying enough': "2019-06-04", 
    'On track': "2019-06-10",
    'Personal issue outside of our control': "2019-06-04",
    'Progression downturn': "2019-05-27",
    'Unmotivated to complete the course': "2019-06-04",
    'Not contactable and inactive': "2019-05-27",
    'Struggling to advance in current module': "2019-06-04",
    'Low confidence': "2019-06-04",
    'Recently found a tech job': "2019-06-04",
    'Unable to advance effectively on the course': "2019-05-27",
    'Ineffective learning approach': "2019-05-27",
    'Long term inactive - warned': "2019-06-04"
}

def auth_headers(access_token):
    return {"Authorization": "Zoho-oauthtoken " + access_token}


def get_access_token():
    refresh_resp = requests.post(REFRESH_ENDPOINT, params={
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    })
    return refresh_resp.json()['access_token']


def get_activities(token, criteria):
    
    page=0
    records=[]
    while True:
        activities_resp = requests.get(
            ACTIVITIES_ENDPOINT + '/search',
            params={
                "criteria": criteria,
                "per_page": MAX_PER_PAGE,
                "page": page
            },
            headers=auth_headers(token)
        )
            
        records += activities_resp.json()
        if not activities_resp.json()['info']['more_records']:
            break
        page += 1
    return activities_resp.json()['data']

def extract_open_activities(activities):
    ids = []
    for activity in activities:
        if activity['Status'] == "Not Started":
            ids.append(activity['id'])
    return ids

def update_open_activity(activity_id, date):
    activity_resp = requests.put(
        ACTIVITIES_ENDPOINT,
        json={"data": [{"id": activity_id, "Start_Date": date}]},
        headers=auth_headers(token))
    print(activity_resp.json())


if __name__ == "__main__":
    token = get_access_token()
    with open('students_ids_by_barometer.json','r') as f:
        student_ids_by_barometer = json.load(f)
        f.close()
    high_risk_statuses = [
        'New student',
        'Missed project submission',
        'Other',
        'Long term inactive'
    ]
    
    for key in list(student_ids_by_barometer):
        if key in high_risk_statuses:
            student_ids_by_barometer.pop(key, None)
    data = student_ids_by_barometer

    with open('students_ids_by_barometer.json','w') as f:
        json.dump(data, f)
        f.close()

    for key, value in student_ids_by_barometer.items():
        if key == 'Recently found a tech job':
            dnc_date = DATES[key]
            student_ids = value
            for id in student_ids:
                activities=get_activities(token, criteria = f'(Who_Id:equals:{id})')
                open_activities = extract_open_activities(activities)
                if len(open_activities) == 1:
                    update_open_activity(open_activities[0], dnc_date)
                else:
                    with open('problem.txt','a') as f:
                        f.write(id + '\n')
                        f.close()

    