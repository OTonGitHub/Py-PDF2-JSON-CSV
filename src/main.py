## For Jupyter Notebook
# !python3 -m pip install --upgrade --no-cache-dir -U pip --prefer-binary
# !python3 -m pip install --no-cache-dir -U PyPDF2 --prefer-binary
# !python3 -m pip install --no-cache-dir -U pandas --prefer-binary

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
output_dir_json = os.path.abspath(os.path.join("JSON-output"))
output_dir_csv = os.path.abspath(os.path.join("CSV-output"))

eod = "8th Floor, City Square, Chaandhanee Magu"

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

json_schema = [form_info, collateralization, status_remarks]

# inner_item 1 is start delimiter, inner_item 2 is end delimiter,
# if inner_item 2 is empty, will use next inner_item starting delimited as ending delimiter,
# if last item's inner_item 2 is empty, end delimiter for that item will be EOD
csv_schema  = [ 
    ["Reference Number", ""],
    ["Submitted By", ""],
    ["Employer No", ""],
    ["Employer Name", "Collateralization & Return Info"],
    ["ID Card No", ""],
    ["Full Name", ""],
    ["Ref No", ""],
    ["Collateralized Amount", ""],
    ["Principle Amount", ""],
    ["Balance Amount", ""],
    ["Interest/Income Amount", ""],
    ["Return from Principle Amount", ""],
    ["Date of Return", "Status Remarks"]
]

class FormItemNotFoundExeception(Exception):
    def __init__(self, message="Form Item Not Found"):
        self.message = message
        super().__init__(self.message)

class InvalidInputError(Exception):
    def __init__(self, message="Invalid input"):
        self.message = message
        super().__init__(self.message)

def input_files() -> Generator[str, None, None]:
    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            yield file

# convert to extension method on typed str type
def printing_message(file_name: str):
    print(f"""
  📚 -> CONVERTING: {file_name}""")

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
def convert_json(file_path: str):
    pdf_content = get_pdf_content(file_path)
    pdf_content_length = len(pdf_content)
    json_output = {}
    csp = 0 # cursor start position of pdf content
    for section_index, form_section in enumerate(json_schema):
        key: str = re.sub(r'[{}":]', '', next(iter(form_section)))
        section = {key: []}
        section_start = re.search(f"{form_section[key][0]}", pdf_content).start() # TODO: switch to end + 1 and handle in case_1
        if (section_index != 2):
            section_end   = re.search(f"{next(iter(json_schema[section_index + 1]))}", pdf_content).start() - 1
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

# TODO: append to list asyncrhonously and write from list to disk in batch
def convert_csv(file_path: str):
    pdf_content = get_pdf_content(file_path)
    csv_output = {}
    for index, item in enumerate(csv_schema):
        try:
            delim_start = (re.search(item[0], pdf_content).end() + 1)
            if (delim_start):
                if (index != len(csv_schema) -1): # TODO: LOGIC HACK! CAREFUL  -- REFACTOR REFACTOR TODO: REFACTOR
                    if (item[1] == ""):
                        delim_end = re.search(csv_schema[index + 1][0], pdf_content).start() - 1
                    else:
                        # delim_end = match.start() - 1 if match else None
                        delim_end = re.search(item[1], pdf_content).start() - 1
                else:
                    if (item[1] != ""):
                        delim_end = delim_end = re.search(item[1], pdf_content).start() - 1
                    else:
                        delim_end = re.search(eod, pdf_content).start() - 1
            else:
                # TODO: schange terminatino scope to file only
                raise FormItemNotFoundExeception(f"item: DELIM_START: {item}: NOT FOUND - Program Terminated") # exception overflow
        except:
            # TODO: add delim info and item and form info to err msg
            raise FormItemNotFoundExeception(f"item: DELIM_END: {item}: NOT FOUND - Program Terminated") # fallover exception
        csv_output[item[0]] = pdf_content[delim_start:delim_end].strip() # unhashable if key is list, make sure not indexable aka 1 value.
    return csv_output

# MAIN / TODO: Make Async
output_type = input("Output Type: 1 (JSON) / 2 (CSV): ")

if re.match(r'^[1|J|j]$', output_type, re.IGNORECASE):
    for file in input_files():
        printing_message(file)
        out = convert_json((os.path.join(input_dir, file)))
        with open(os.path.join(output_dir_json, str(uuid.uuid4())+".json"), "w") as json_file:
            json.dump(out, json_file)
# TODO: create lock object on main list and generate add convert to pd DF then batch conver to csv using pd
elif re.match(r'^[2|C|c]$', output_type, re.IGNORECASE):
    out = []
    for file in input_files():
        printing_message(file)
        out.append(convert_csv((os.path.join(input_dir, file))))
    df = pd.DataFrame(out)
    with open(os.path.join(output_dir_csv, str(uuid.uuid4())+".csv"), "w") as csv_file:
        df.to_csv(csv_file, index=False)
else:
    raise InvalidInputError("Wrong input, Restart Program and Follow Instructions.")