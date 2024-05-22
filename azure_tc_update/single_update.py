import requests
import json
import jsonpath
from datetime import datetime

organization = "PakEnergy"
project = "Accounting"
pat = ""
tesPlanName = "2024"
testSuiteName = "Test"
testcaseName = "Test 1" 
# testCaseNames = ["Test 1", "Test 2", "Test 3"] 
outcome = "Failed"
# outcomes = ["Passed", "Failed", "Blocked", "NotExecuted"]


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


def get_testcase_ID():
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


print("test case ID: " + get_testcase_ID())


def get_testpoint_ID():
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


print("Test point ID: " + get_testpoint_ID())


def create_run():
    try:
        runName = tesPlanName + "-" + str(datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
        planId = get_testplan_details()
        pointId = get_testpoint_ID()
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/test/runs?api-version=7.1-preview.3"
        )
        payload = {"name": runName, "plan": {"id": planId}, "pointIds": [pointId]}
        response = requests.post(
            url=url,
            json=payload,
            auth=("", pat),
            headers={"Content-Type": "application/json"},
        )
        reponsejson = json.loads(response.text)

        runID = jsonpath.jsonpath(reponsejson, "$.id")[0]
        return str(runID)
    except Exception as e:
        print("Something went wrong in fetching Run ID :" + str(e))


print("test run ID: " + create_run())


def get_testResult_ID():
    try:
        runID = create_run()
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/test/Runs/"
            + runID
            + "/results?api-version=7.1-preview.6"
        )
        response = requests.get(url=url, auth=("", pat))
        reponsejson = json.loads(response.text)
        resultID = jsonpath.jsonpath(reponsejson, "$.value.[0].id")[0]
        return str(resultID)
    except Exception as e:
        print("Something went wrong in fetching Result ID :" + str(e))


print("test result ID: " + get_testResult_ID())


def update_result(outcome):
    try:
        runId = create_run()
        testResultId = get_testResult_ID()
        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/test/Runs/"
            + runId
            + "/results?api-version=7.1-preview.6"
        )
        payload = [
            {
                "id": int(testResultId),
                "state": "Completed",
                "comment": "Website theme is looking good",
                "outcome": outcome,
            }
        ]

        resp = requests.patch(
            url,
            json=payload,
            auth=("", pat),
            headers={"Content-Type": "application/json"},
        )
        print(resp.status_code)
        print(
            'the test cases --> "'
            + testcaseName
            + '" has been updated with the result '
            + outcome.upper()
            + " successfully"
        )
    except Exception as e:
        print("Something went wrong in updating Test Results :" + str(e))


update_result(outcome)
