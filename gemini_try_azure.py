import requests
import json
import jsonpath
from datetime import datetime

# Azure DevOps Configuration
organization = "PakEnergy"
project = "Accounting"
pat = ""
tesPlanName = "2024"
testSuiteName = "Test"
testCaseNames = ["Test 1", "Test 2", "Test 3"]  # Multiple test cases
outcomes = ["Passed", "Failed", "Blocked", "NotExecuted"]

# Helper Functions (get_testplan_details, get_testsuite_details, get_testcase_ID remain the same)
# ... (your existing code for these functions)
def get_testplan_details():
    try:
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/testplan/plans?api-version=7.2-preview.1"
        )
        response = requests.get(url=url, auth=("", pat))
        reponsejson = json.loads(response.text)
        planID = jsonpath.jsonpath(
            reponsejson, "$.value.[?(@.name == '" + tesPlanName + "')].id"
        )[0]

        return str(planID)
    except Exception as e:
        print("Something went wrong in fetching Test Plan ID :" + str(e))


print("test Plan id: " + get_testplan_details())

def get_testsuite_details():
    try:
        planid = get_testplan_details()
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/testplan/Plans/"
            + planid
            + "/suites?api-version=7.1-preview.1"
        )
        response = requests.get(url=url, auth=("", pat))
        reponsejson = json.loads(response.text)
        suiteID = jsonpath.jsonpath(
            reponsejson, "$.value.[?(@.name == '" + testSuiteName + "')].id"
        )[0]
        return str(suiteID)
    except Exception as e:
        print("Something went wrong in fetching Test Suite ID :" + str(e))


print("test suite id: " + get_testsuite_details())

def get_testcase_ID(testcaseName):
    try:
        planID = get_testplan_details()
        suiteID = get_testsuite_details()
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/testplan/Plans/"
            + planID
            + "/Suites/"
            + suiteID
            + "/TestCase?api-version=7.1-preview.3"
        )
        response = requests.get(url=url, auth=("", pat))
        # print(response.text)
        reponsejson = json.loads(response.text)
        testcaseID = jsonpath.jsonpath(
            reponsejson,
            "$.value[?(@.workItem.name == '" + testcaseName + "')].workItem.id",
        )[0]
        return str(testcaseID)
    except Exception as e:
        print("Something went wrong in fetching Test Case ID :" + str(e))


# print("test case ID: " + get_testcase_ID(testcaseName))

def get_testpoint_ID(tcID):
    try:
        planID = get_testplan_details()
        suiteID = get_testsuite_details()
        tcID = get_testcase_ID()
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/testplan/Plans/"
            + planID
            + "/Suites/"
            + suiteID
            + "/TestPoint?testCaseId="
            + tcID
            + "&api-version=7.1-preview.2"
        )
        response = requests.get(url=url, auth=("", pat))
        reponsejson = json.loads(response.text)
        testpointID = jsonpath.jsonpath(reponsejson, "$.value[0].id")[0]
        return str(testpointID)
    except Exception as e:
        print("Something went wrong in fetching Test Point ID :" + str(e))


#print("Test point ID: " + get_testpoint_ID())

def create_run_and_update_results():
    try:
        runName = tesPlanName + "-" + str(datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
        planId = get_testplan_details()
        suiteId = get_testsuite_details()

        # Get Test Point IDs for all Test Cases
        pointIds = []
        for testCaseName in testCaseNames:
            tcId = get_testcase_ID(testCaseName)
            pointId = get_testpoint_ID(tcId)
            pointIds.append(pointId)

        # Create the Run
        url = f"https://dev.azure.com/{organization}/{project}/_apis/test/runs?api-version=7.1-preview.3"
        payload = {"name": runName, "plan": {"id": planId}, "pointIds": pointIds}
        response = requests.post(url, json=payload, auth=("", pat), headers={"Content-Type": "application/json"})
        response_json = json.loads(response.text)
        runId = response_json["id"]

        # Get Test Result IDs and Update Results
        url = f"https://dev.azure.com/{organization}/{project}/_apis/test/Runs/{runId}/results?api-version=7.1-preview.6"
        response = requests.get(url, auth=("", pat))
        response_json = json.loads(response.text)
        resultIds = [result["id"] for result in response_json["value"]]

        if len(resultIds) != len(outcomes):
            raise Exception("Mismatch in number of results and outcomes")

        payload = []
        for resultId, outcome in zip(resultIds, outcomes):
            payload.append({
                "id": resultId,
                "state": "Completed",
                "comment": "Updated in bulk",
                "outcome": outcome
            })

        resp = requests.patch(url, json=payload, auth=("", pat), headers={"Content-Type": "application/json"})

        if resp.status_code == 200:
            print("Test results updated successfully!")
        else:
            print(f"Error updating results: {resp.text}")

    except Exception as e:
        print(f"Something went wrong: {e}")

# Execute the main function
create_run_and_update_results()
