import requests
import json
import urllib.parse
import xml.etree.ElementTree as ET
import os
import re

# 3 fields below used for initializing Controller class
account_name_input = "sammons"
username_input = ""
password_input = ""    # Client Name field in UI
# below variable takes file with AppDynamics application IDs as input. Each line has a new app name, no delimiter
app_ids_txt_file = "/Users/aaronjacobs/Desktop/action_suppress_SAMMONS/app_ids.txt"
# below JSON file takes the JSON payload that creates the action suppression
# https://docs.appdynamics.com/appd/21.x/21.1/en/extend-appdynamics/appdynamics-apis/alert-and-respond-api
action_suppression_json_payload_file = "/Users/aaronjacobs/Desktop/action_suppress_SAMMONS/action_suppress.json"


class Controller:
    def __init__(self, account_name: str, username: str, password: str):
        self.account_name = None
        self.username = None
        self.password = None
        self.controller_headers = None
        self.controller_url = None
        self.un_at_account = None
        self.auth = None
        self.update(account_name=account_name, username=username, password=password)

    def update(self, account_name: str, username: str, password: str):
        self.account_name = account_name
        self.username = username
        self.password = password
        self.controller_url = "https://{}.saas.appdynamics.com".format(account_name)
        self.un_at_account = username + "@" + account_name
        self.auth = ('{}@{}'.format(self.username, self.account_name), self.password)


def get_apm_apps(app_ids_filename):
    bus_app_resp = requests.get(my_connection.controller_url + '/controller/rest/applications?output=JSON',
                                auth=my_connection.auth)
    json_resp = json.loads(bus_app_resp.content.decode('utf-8'))
    app_dict = {}
    app_counter = 0
    if app_ids_filename:
        with open(app_ids_filename, 'w') as f:
            for item in json_resp:
                app_element = json_resp[app_counter]
                app_id = str(app_element["id"])
                app_name = app_element["name"]

                # below yields app_name=value, app_id=key
                app_dict[app_id] = app_name
                print( app_id, "\t", app_name)
                f.write(app_id)
                f.write('\n')
                app_counter += 1
    else:
        with open(app_ids_filename, 'w') as f:
            for item in json_resp:
                app_element = json_resp[app_counter]
                app_id = str(app_element["id"])
                app_name = app_element["name"]

                # below yields app_name=value, app_id=key
                app_dict[app_id] = app_name
                print( app_id, "\t", app_name)
                f.write(app_id)
                f.write('\n')
                app_counter += 1

    return app_dict


def create_action_suppression(json_filename, app_names_file, url_in):
    with open(app_names_file) as file:
        for app_name in file:
            app_name = app_name.rstrip()
            app_id_only = re.sub(r'\s.*', '', app_name)
            print(app_id_only)

            with open(json_filename) as json_data:
                url = url_in + "/controller/alerting/rest/v1/applications/{}/action-suppressions".format(app_id_only)
                print("url: ", url)
                d = json.load(json_data)
                print("d: ", d)
                r = requests.post(url, auth=my_connection.auth, json=d)
                print(r.status_code)
                print(r.text)
                print()


# GET /controller/api/accounts/account_id/applications/application_id/actionsuppressions
def retrieve_all_action_supps(acc_id, app_name):
    act_resp = requests.get(
        my_connection.controller_url + '/controller/api/accounts/{}/applications/{}/actionsuppressions'.format(acc_id, app_name),
        auth=my_connection.auth)
    json_resp = json.loads(act_resp.content.decode('utf-8'))
    if "actionSuppressions" in json_resp:
        act_supp_root = json_resp["actionSuppressions"]
        act_supp_root_counter = 0
        for item in act_supp_root:
            element = act_supp_root[act_supp_root_counter]
            id = element['id']
            name = element['name']
            time_range = element['timeRange']
            affects = element['affects']
            print('id: ', id)
            print('name: ', name)
            print('time range: ', time_range)
            print('affects: ', affects)
            print()
            act_supp_root_counter += 1
    else:
        print("No action suppressions exist for this app, exiting...")


# GET /controller/api/accounts/account_id/applications/application_id/actionsuppressions
def retrieve_specfic_action_supp_by_id(acc_id, app_id, supp_id):
    conn_str = mc.url + '/controller/api/accounts/{}/applications/{}/actionsuppressions/{}'.format(acc_id, app_id,
                                                                                                   supp_id)
    print('url str: ', conn_str)
    act_resp = requests.get(
        conn_str,
        auth=(mc.user_at_account_name, mc.pw))
    print("resp content: ", act_resp.content)
    print("resp: ", act_resp)
    print("resp status code: ", act_resp.status_code)
    json_resp = json.loads(act_resp.content.decode('utf-8'))
    print('json resp: ', json_resp)
    # act_root = json_resp["actions"]
    # print("act root: ", act_root)

    print("id: ", json_resp['id'])
    print("name: ", json_resp['name'])
    print("time range: ", json_resp['timeRange'])
    print("hr ids: ", json_resp['healthRuleIds'])
    print("affects: ", json_resp['affects'])
    # id = element['id']
    # name = element['name']
    # time_range = element['timeRange']
    # hr_ids = element['healthRuleIds']
    # affects = element['affects']

    # print('id: ', id)
    # print('name: ', name)
    # print('time range: ', time_range)
    # print('hr_ids: ', hr_ids)
    # print('affects: ', affects)
    # act_supp_root_counter += 1


# DELETE /controller/api/accounts/account_id/applications/application_id/actionsuppressions/actionsuppression_id
def delete_action_suppressions(acc_id, supp_id, app_names_file):
        with open(app_names_file) as file:
            for app_name in file:
                app_name = app_name.rstrip()
                app_id_only = re.sub(r'\s.*', '', app_name)
                print(app_id_only)

                conn_str = my_connection.controller_url + '/controller/api/accounts/{}/applications/{}/actionsuppressions/{}'\
                    .format(acc_id, app_id_only, supp_id)
                print(conn_str)
                r = requests.delete(conn_str, auth=my_connection.auth)
                print("response status code: ", r.status_code)
                print("resp text: ", r.text)
                if r.status_code == 204:
                    print("action suppression sucessfully deleted.  Hard refresh action supp screen to see it gone... ")


# DELETE /controller/api/accounts/account_id/applications/application_id/actionsuppressions/actionsuppression_id
def delete_specific_action_supp_by_id(acc_id, app_id, supp_id):
    conn_str = my_connection.controller_url + '/controller/api/accounts/{}/applications/{}/actionsuppressions/{}'.format(acc_id, app_id,
                                                                                                   supp_id)
    print("url: ", conn_str)
    r = requests.delete(conn_str, auth=my_connection.auth)
    print("resp content: ", r.content)
    print("resp: ", r)
    print("resp status code: ", r.status_code)
    if r.status_code == 204:
        print("action suppression sucessfully deleted.  Hard refresh action supp screen to see it gone... ")


def get_account_id():
    resp = requests.get(my_connection.controller_url + '/controller/api/accounts/myaccount', auth=my_connection.auth)
    json_resp = json.loads(resp.content.decode('utf-8'))
    accountId = json_resp['id']
    # print("acc ID: " + accountId)
    return accountId


def print_menu():
    print(30 * "-", "MENU", 30 * "-")
    print("0. Exit")
    print("1. Menu Option 1 - Create Action Suppression")
    print("2. Menu Option 2 - Delete Action Suppression by ID")
    print("3. Menu Option 3 - Retrieve All Action Suppressions")
    print("4. Menu Option 4 - Create applications text file")
    print("5. Menu Option 5 - Create Action Suppressions for WAS apps")
    print("6. Menu Option 6 - Create Action Suppressions for Tomcat apps")
    print("7. Menu Option 7 - Create Action Suppressions for DotNet apps")
    print(77 * "-")


def menu():
    loop = True
    while loop:  ## While loop which will keep going until loop = False
        print_menu()  ## Displays menu
        choice = input("Enter your choice [1-10]: ")
        if choice == "0":
            loop = False
        elif choice == "1":
            print("1 has been selected - Create Action Suppression")
            create_action_suppression(action_suppression_json_payload_file, app_ids_txt_file, url)
        elif choice == "2":
            print("2 has been selected - Delete Action Suppression by ID")
            suppression_id = input("enter suppression ID: ")
            app_names_file_in = input("Enter path to file with application IDs (WAS/Tomcat/DotNet): ")
            delete_action_suppressions(account_id, suppression_id, app_names_file_in)
        elif choice == "3":
            print("3 has been selected - Retrieve All Action Suppressions")
            app_id = input("Enter app ID to show all Action Suppressions: ")
            retrieve_all_action_supps(account_id, app_id)
        elif choice == "4":
            print("4 has been selected - Create applications text file")
            get_apm_apps(app_ids_txt_file)
        elif choice == "5":
            print("5 has been selected - Create Action Suppressions for WAS apps")
            create_action_suppression("action_suppress.json", "app_ids_was.txt", url)
        elif choice == "6":
            print("6 has been selected - Create Action Suppressions for Tomcat apps")
            create_action_suppression("action_suppress.json", "app_ids_tomcat.txt", url)
        elif choice == "7":
            print("7 has been selected - Create Action Suppressions for DotNet apps")
            create_action_suppression("action_suppress.json", "app_ids_dotnet.txt", url)


my_connection = Controller(account_name_input, username_input, password_input)
un_at_an = my_connection.un_at_account
pw = my_connection.password
url = my_connection.controller_url
account_id = get_account_id()

# menu()
delete_specific_action_supp_by_id(account_id, "1216081", "9")

# get_apm_apps("app_ids.txt")
# create_action_suppression_new(action_suppression_json_payload_file, app_ids_txt_file, url)
# retrieve_all_action_supps(account_id, "11846")





