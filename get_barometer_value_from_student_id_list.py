import requests
import json
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
        STUDENTS_ENDPOINT + "/" + id,
        params={"per_page": 1},
        headers=auth_headers(token))
    if student_resp.status_code != 200:
        print("Fail! Could not find student record with this id: ", id)
    student = student_resp.json()['data'][0]
    return student['Last_Barometer_Value']


if __name__ == "__main__":
    token = get_access_token()
    student_ids_by_barometer = {}
    for id in ids:
        barometer = get_student(token, id)
        if barometer in student_ids_by_barometer.keys():
            student_ids_by_barometer[barometer].append(id)
        else:
            student_ids_by_barometer[barometer] = [id]
    with open('students_ids_by_barometer.json','w') as fp:
        json.dump(student_ids_by_barometer, fp)
        fp.close()
