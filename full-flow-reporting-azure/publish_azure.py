import xml.etree.ElementTree as ET
import requests
import json
import jsonpath
from datetime import datetime
import argparse

def extract_test_case_data(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Create lists for the test case names and results
    test_case_names = []
    test_case_results = []

    # Iterate over the 'testcase' elements
    for testcase in root.iter("testcase"):
        # Get the name attribute
        name = testcase.get("name")
        test_case_names.append(name)

        # Check for 'error' elements in the testcase
        result = "Passed" if testcase.find("error") is None else "Failed"
        test_case_results.append(result)

    return test_case_names, test_case_results

parser = argparse.ArgumentParser(description='Process a JUnit report.')
parser.add_argument('report_path', help='The path to the JUnit report.')
# Use the function
#test_case_names, test_case_results = extract_test_case_data("parsed_report.junit.xml")
args = parser.parse_args()
testcaseNames, outcomes = extract_test_case_data(args.report_path)
#testcaseNames, outcomes = extract_test_case_data("parsed_report.junit.xml")
print(testcaseNames)
print(outcomes)
organization = "PakEnergy"
project = "Accounting"
pat = ""
testPlanName = "2024"
testSuiteName = "Test"

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
            reponsejson, "$.value.[?(@.name == '" + testPlanName + "')].id"
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


def get_testcase_IDs():
    testcaseIDs = []
    for testcaseName in testcaseNames:
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

            reponsejson = json.loads(response.text)
            testcaseID = jsonpath.jsonpath(
                reponsejson,
                "$.value[?(@.workItem.name == '" + testcaseName + "')].workItem.id",
            )[0]
            testcaseIDs.append(str(testcaseID))
        except Exception as e:
            print("Something went wrong in fetching Test Case ID :" + str(e))
    return testcaseIDs


print(", ".join(str(x) for x in get_testcase_IDs()))


def get_testpoint_IDs():
    testpointIDs = []
    planID = get_testplan_details()
    suiteID = get_testsuite_details()
    for testcaseID in get_testcase_IDs():
        try:

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
                + testcaseID
                + "&api-version=7.1-preview.2"
            )
            response = requests.get(url=url, auth=("", pat))
            reponsejson = json.loads(response.text)
            testpointID = jsonpath.jsonpath(reponsejson, "$.value[0].id")[0]
            testpointIDs.append(str(testpointID))
        except Exception as e:
            print("Something went wrong in fetching Test Point ID :" + str(e))
    return testpointIDs


print(", ".join(str(x) for x in get_testpoint_IDs()))


def create_run():
    try:
        runName = testPlanName + "-" + str(datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
        planId = get_testplan_details()
        pointIds = get_testpoint_IDs()

        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/test/runs?api-version=7.1-preview.3"
        )
        payload = {"name": runName, "plan": {"id": planId}, "pointIds": pointIds}

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


runID = create_run()
print("Run ID: " + runID)


def get_testResult_IDs():
    resultIDs = []

    try:

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
        count = jsonpath.jsonpath(reponsejson, "$.count")[0]
        for i in range(count):
            resultID = jsonpath.jsonpath(reponsejson, "$.value.[" + str(i) + "].id")[0]
            resultIDs.append(resultID)
    except Exception as e:
        print("Something went wrong in fetching Result ID :" + str(e))
    return resultIDs


print(", ".join(str(x) for x in get_testResult_IDs()))


def update_results():
    runId = runID

    try:

        url = (
            "https://dev.azure.com/"
            + organization
            + "/"
            + project
            + "/_apis/test/Runs/"
            + runId
            + "/results?api-version=7.1-preview.6"
        )
        payload = []
        for testResultId, outcome in zip(get_testResult_IDs(), outcomes):
            payload.append(
                {
                    "id": int(testResultId),
                    "state": "Completed",
                    "comment": "THIS OUTCOME WAS SET USING TEST AUTOMATION",
                    "outcome": outcome,
                }
            )

        resp = requests.patch(
            url,
            json=payload,
            auth=("", pat),
            headers={"Content-Type": "application/json"},
        )
        print(resp.status_code)

    except Exception as e:
        print("Something went wrong in updating Test Results :" + str(e))


update_results()