## For Jupyter Notebook
# !python3 -m pip install --upgrade --no-cache-dir -U pip --prefer-binary
# !python3 -m pip install --no-cache-dir -U PyPDF2 --prefer-binary
# !python3 -m pip install --no-cache-dir -U pandas --prefer-binary

# for non Jupyter environment, just remove the "!" from the above commands
# if on unix/mac, replace python3 with python (depends, try python first, if not working, try python3)

# READ README.md

import os
from typing import Generator
import pandas as pd
import PyPDF2 as pdf
import re
from pprint import pprint
import json
import uuid

input_dir = os.path.abspath(os.path.join("PDF-input"))
output_dir = os.path.abspath(os.path.join("JSON-output"))

form_info = {
    "Collateralization Returns": [ # strips "Employer Info" and flattens section
        "Reference Number", 
        "Submitted By", 
        "Employer No", 
        "Employer Name"
    ]}

collateralization = { # appends each return info section iterating number
    "Collateralization & Return Info": [
        "ID Card No", 
        "Full Name", 
        "Ref No", 
        "Collateralized Amount",
        "Principle Amount",
        "Balance Amount",
        "Interest/Income Amount",
        "Return from Principle Amount",
        "Date of Return"
    ]}

status_remarks = { # assumed, only "By" & "Date" in each section
    "Status Remarks": [
        "Pending Approval",
        "Approved",
        "Submitted"
    ]}

form_schema = [form_info, collateralization, status_remarks]

class FormItemNotFoundExeception(Exception):
    def __init__(self, message="Form Item Not Found"):
        self.message = message
        super().__init__(self.message)

def input_files() -> Generator[str, None, None]:
    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            yield file

def get_pdf_content(file_path: str) -> str:
    # print(file_path)
    pdf_content: str = "" # CONTENT OF PDF
    try:
        with open(file_path, "rb") as pdf_file:
            pdf_reader = pdf.PdfReader(pdf_file)
            count = 0;
            for page in range(len(pdf_reader.pages)):
                page_content = pdf_reader.pages[page].extract_text()
                count += 1
                pdf_content += page_content
    except Exception as err:
        print(f"Error: {err}")
    with open('READ_DATA_TESTING.txt', 'w') as file:
        file.write(pdf_content.replace("Employer Info", "", 1))
    return pdf_content.replace("Employer Info", "", 1)

def section_seeker (schema_reference, section_data):
    data = []
    for index, form_item in enumerate(schema_reference):            
        delim_start = re.search(f"{form_item}", section_data).end() + 1
        if delim_start:
            if (index == len(schema_reference) - 1):
                delim_end = len(section_data)
            else:
                delim_end = re.search(f"{schema_reference[index + 1]}", section_data).start() - 1
            data.append(
                { form_item: section_data[delim_start:delim_end].strip() }
            )
        else:
            raise FormItemNotFoundExeception(f"FORM ITEM [{form_item}] NOT FOUND, HENCE OPETATION ABORTED, (in next version, this will be applied file by file)")
    return data

def case_3(schema_reference, section_data):
    data = {}
    for index, form_item in enumerate(schema_reference):
        inner_data = []
        delim_start = re.search(f"{form_item}", section_data).end() + 1
        if (index == len(schema_reference) - 1):        
            delim_end = len(section_data)
        else:
            delim_end = re.search(f"{schema_reference[index + 1]}", section_data).start() - 1
        inner_data.append(section_seeker(["By","Date"], section_data[delim_start:delim_end]))
        data[form_item] = inner_data
    return data

# TODO: MAKE ASYNC
def conversion(file_path: str):
    pdf_content = get_pdf_content(file_path)
    pdf_content_length = len(pdf_content)
    json_output = {}
    csp = 0 # cursor start position of pdf content
    for section_index, form_section in enumerate(form_schema):
        key: str = re.sub(r'[{}":]', '', next(iter(form_section)))
        section = {key: []}
        section_start = re.search(f"{form_section[key][0]}", pdf_content).start() # TODO: switch to end + 1 and handle in case_1
        if (section_index != 2):
            section_end   = re.search(f"{next(iter(form_schema[section_index + 1]))}", pdf_content).start() - 1
        else:
            section_end   = re.search("8th Floor, City Square, Chaandhanee Magu", pdf_content).start() - 1
        switch_case = {
                1: lambda schema_reference, section_data: section_seeker(schema_reference, section_data),
                2: lambda schema_reference, section_data: section_seeker(schema_reference, section_data), # overflow 2 -> 1 | actually 2 needs own case, later
                3: lambda schema_reference, section_data: case_3(schema_reference, section_data)
            }
        value = switch_case.get(section_index + 1)(form_section[key], pdf_content[section_start:section_end])
        json_output[key] = value
    return json_output

# MAIN / TODO: Make Async
for file in input_files():
    print(f"""
          [ Initiated Conversion of {file} ]""")
    out = conversion((os.path.join(input_dir, file)))
    with open(os.path.join(output_dir, str(uuid.uuid4())+".json"), "w") as json_file:
        json.dump(out, json_file)