import json

import xml.etree.ElementTree as ET


def translate_test_case_names(file_path, translation_dict):
    # Parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Iterate over the 'testcase' elements
    for testcase in root.iter("testcase"):
        # Get the name attribute
        name = testcase.get("name")
        # Translate the name
        translated_name = translation_dict.get(name, name)
        # Replace the old name with the translated one
        testcase.set("name", translated_name)

    # Write the changes back to the file
    tree.write("parsed_report.junit.xml")


# Load the translation dictionary from the JSON file
with open("translation_tc_names_ranorex_azure.json", "r") as f:
    translation_dict = json.load(f)

# Use the function
translate_test_case_names("Ranorex Results.rxlog.junit.xml", translation_dict)
