import requests
import math
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


def batch_update(token, student_id_list, field_to_be_updated, additional_field_to_be_updated, new_value):
    print("Number of student ids: ", len(student_id_list))
    if len(student_id_list) > 100:
        student_id_sublists = create_sublists(student_id_list)

        for student_id_sublist in student_id_sublists:
            update_field(token, student_id_sublist, field_to_be_updated, additional_field_to_be_updated, new_value)
    else:
        update_field(token, student_id_list, field_to_be_updated, additional_field_to_be_updated, new_value)



def update_field(token, student_ids, field_to_be_updated, additional_field_to_be_updated, new_value):
    update_resp = requests.put(
        STUDENTS_ENDPOINT,
        json={
            "data": [{"id": student_id, field_to_be_updated: new_value, additional_field_to_be_updated: new_value} 
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


if __name__ == "__main__":
    token = get_access_token()
    batch_update(token, ids, 'Tutor_Template', 'Assigned_Tutor', '')
