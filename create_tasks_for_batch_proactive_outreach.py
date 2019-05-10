import requests
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


def get_student(token, id):
    student_resp = requests.get(
        f'{STUDENTS_ENDPOINT}/{id}',
        params={"per_page": 1},
        headers=auth_headers(token))
    if student_resp.status_code != 200:
        print("Fail! Could not find student record with this id: ", id)
    student = student_resp.json()['data'][0]
    return {
        'id': id,
        'Barometer': student['Last_Barometer_Value'],
        'Progression_Status': student['Last_Progression_Status']
    }


def create_an_activity(token, student_data, tutor, subject, start_date):

    fields = {
        "Subject": subject,
        "Progression_Status": student_data['Progression_Status'],
        "Barometer": student_data['Barometer'],
        "Who_Id": student_data['id'],
        "Start_Date": start_date,
        "Owner": TUTOR_CONTACT_IDS[tutor],
        "Status": "Completed"
    }
    activity_resp = requests.post(
        ACTIVITIES_ENDPOINT,
        json={"data": [fields]},
        headers=auth_headers(token))
    print(activity_resp)


if __name__ == "__main__":
    token = get_access_token()
    for id in ids:
        create_an_activity(token, get_student(token, id), 'TUTORNAME', 'Slack Reengagement', "2019-05-10")
