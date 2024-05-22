import requests
import json
import jsonpath
from datetime import datetime

organization = "PakEnergy"
project = "Accounting"
pat = ""
tesPlanName = "2024"
testSuiteName = "Test"
testCaseNames = ["Test 1", "Test 2", "Test 3"]
outcomes = ["Passed", "Failed", "Passed"]

def get_testplan_details():
    try:
        url = f"https://dev.azure.com/{organization}/{project}/_apis/testplan/plans?api-version=7.2-preview.1"
        response = requests.get(url=url, auth=("", pat))
        response_json = response.json()
        plan_id = jsonpath.jsonpath(response_json, f"$.value.[?(@.name == '{tesPlanName}')].id")[0]
        return str(plan_id)
    except Exception as e:
        print(f"Something went wrong in fetching Test Plan ID: {e}")

def get_testsuite_details():
    try:
        plan_id = get_testplan_details()
        url = f"https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{plan_id}/suites?api-version=7.1-preview.1"
        response = requests.get(url=url, auth=("", pat))
        response_json = response.json()
        suite_id = jsonpath.jsonpath(response_json, f"$.value.[?(@.name == '{testSuiteName}')].id")[0]
        return str(suite_id)
    except Exception as e:
        print(f"Something went wrong in fetching Test Suite ID: {e}")

def get_testcase_ID(testcase_name):
    try:
        plan_id = get_testplan_details()
        suite_id = get_testsuite_details()
        url = f"https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{plan_id}/Suites/{suite_id}/TestCase?api-version=7.1-preview.3"
        response = requests.get(url=url, auth=("", pat))
        response_json = response.json()
        testcase_id = jsonpath.jsonpath(response_json, f"$.value[?(@.workItem.name == '{testcase_name}')].workItem.id")[0]
        return str(testcase_id)
    except Exception as e:
        print(f"Something went wrong in fetching Test Case ID: {e}")

def get_testpoint_ID(testcase_id):
    try:
        plan_id = get_testplan_details()
        suite_id = get_testsuite_details()
        url = f"https://dev.azure.com/{organization}/{project}/_apis/testplan/Plans/{plan_id}/Suites/{suite_id}/TestPoint?testCaseId={testcase_id}&api-version=7.1-preview.2"
        response = requests.get(url=url, auth=("", pat))
        response_json = response.json()
        testpoint_id = jsonpath.jsonpath(response_json, "$.value[0].id")[0]
        return str(testpoint_id)
    except Exception as e:
        print(f"Something went wrong in fetching Test Point ID: {e}")

def create_run(point_ids):
    try:
        run_name = f"{tesPlanName}-{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}"
        plan_id = get_testplan_details()
        url = f"https://dev.azure.com/{organization}/{project}/_apis/test/runs?api-version=7.1-preview.3"
        payload = {"name": run_name, "plan": {"id": plan_id}, "pointIds": point_ids}
        response = requests.post(url=url, json=payload, auth=("", pat), headers={"Content-Type": "application/json"})
        response_json = response.json()
        run_id = jsonpath.jsonpath(response_json, "$.id")[0]
        return str(run_id)
    except Exception as e:
        print(f"Something went wrong in creating the test run: {e}")

def update_results(run_id, test_results):
    try:
        url = f"https://dev.azure.com/{organization}/{project}/_apis/test/Runs/{run_id}/results?api-version=7.1-preview.6"
        response = requests.patch(url=url, json=test_results, auth=("", pat), headers={"Content-Type": "application/json"})
        print(response.status_code)
        print(f"The test cases have been updated with their results successfully")
    except Exception as e:
        print(f"Something went wrong in updating Test Results: {e}")

def main():
    test_results = []
    point_ids = []
    
    for testcase_name, outcome in zip(testCaseNames, outcomes):
        testcase_id = get_testcase_ID(testcase_name)
        testpoint_id = get_testpoint_ID(testcase_id)
        point_ids.append(int(testpoint_id))
        test_results.append({
            "id": int(testcase_id),
            "state": "Completed",
            "comment": "Test case result updated",
            "outcome": outcome,
        })

    run_id = create_run(point_ids)
    update_results(run_id, test_results)

if __name__ == "__main__":
    main()
