import math
import requests
from emails import emails
from tutor_ids import TUTOR_CONTACT_IDS
from ids import *

CLIENT_ID = XXX
CLIENT_SECRET = XXX
REFRESH_TOKEN = XXX
REFRESH_ENDPOINT = "https://accounts.zoho.com/oauth/v2/token"
STUDENTS_ENDPOINT = "https://www.zohoapis.com/crm/v2/contacts"
ACTIVITIES_ENDPOINT = "https://www.zohoapis.com/crm/v2/tasks"
USERS_ENDPOINT = "https://www.zohoapis.com/crm/v2/users"
MAX_PER_PAGE = 200

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


def batch_update(token, student_id_list, field_to_be_updated, new_value):
    print("Number of student ids: ", len(student_id_list))
    if len(student_id_list) > 100:
        student_id_sublists = create_sublists(student_id_list)

        for student_id_sublist in student_id_sublists:
            update_field(token, student_id_sublist, field_to_be_updated, new_value)
    else:
        update_field(token, student_id_list, field_to_be_updated, new_value)



def update_field(token, student_ids, field_to_be_updated, new_value):
    update_resp = requests.put(
        STUDENTS_ENDPOINT,
        json={
            "data": [{"id": student_id, field_to_be_updated: new_value}
                     for student_id in student_ids]
        },
        headers=auth_headers(token))
    print(update_resp.json())
    return update_resp.status_code == 200


def create_sublists(student_id_list):
    number_of_sublists = math.ceil(len(student_id_list)/100)

    sublists = []

    for i in range(number_of_sublists):
        list_name = "sublist" + str(i+1)
        start_index = i*100
        end_index = start_index + 100
        sublists.append(student_id_list[start_index:end_index])
        print(list_name, " created")

    print("Number of sublists: ", len(sublists))
    return sublists

def get_student_id(token, student_email):
    student_resp = requests.get(
        STUDENTS_ENDPOINT + '/search',
        params={"email": student_email, "per_page": 1},
        headers=auth_headers(token))
    if student_resp.status_code != 200:
        print("Fail! Could not find student record with this email: ", student_email)
    student = student_resp.json()['data'][0]
    return student['id']

def create_an_activity(token, student_data, tutor):

    fields = {
        "Subject": "Tutor reengagement email",
        "Progression_Status": student_data['Progression_Status'],
        "Barometer": student_data['Barometer'],
        "Who_Id": student_data['Who_Id'],
        "Start_Date": "2019-05-15",
        "Owner": TUTOR_CONTACT_IDS[tutor],
        "Status": "Completed"
    }
    activity_resp = requests.post(
        ACTIVITIES_ENDPOINT,
        json={"data": [fields]},
        headers=auth_headers(token))
    print(activity_resp)

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
    print(activity_resp)


if __name__ == "__main__":
    token = get_access_token()
    ACTIVITIES_TO_UPDATE = {
        "2019-04-29": APRIL_TWENTYNINE,
        "2019-04-30": APRIL_THIRTY,
        "2019-05-01": MAY_ONE,
        "2019-05-02": MAY_TWO,
        "2019-05-03": MAY_THREE,
        "2019-05-07": MAY_SEVEN,
        "2019-05-08": MAY_EIGHT,
        "2019-05-09": MAY_NINE,
        "2019-05-10": MAY_TEN,
        "2019-05-13": MAY_THIRTEEN,
        "2019-05-14": MAY_FOURTEEN,
        "2019-05-15": MAY_FIFTEEN,
        "2019-05-16": MAY_SIXTEEN,
        "2019-05-17": MAY_SEVENTEEN
        }
    for date in ACTIVITIES_TO_UPDATE:
        for id in ACTIVITIES_TO_UPDATE[date]:
            activities=get_activities(token, criteria = f'(Who_Id:equals:{id})')
            open_activities = extract_open_activities(activities)
            if len(open_activities) == 1:
                update_open_activity(open_activities[0], date)
            else:
                with open('problem.txt','a') as f:
                    f.write(id + '\n')
                    f.close()
