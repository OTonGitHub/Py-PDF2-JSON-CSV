## Run These Commands First:


## Project Structure:


## Description:
Put all PDF files in PDF-input folder
content inside JSON-output will be deleted,
and all pdf files will be converted to json and output there.

ForNow, every JSON will have a guid,
as file type specific naming is out of scope and rapid dev focus on business logic.

## Ignored Objects:
- contents of PDF and JSONs, the folders are comitted but not the content
- .venv scripts are comitted as well
- pip package downloads inside script are ignored



# TODO: TRIGGERS EXCEPTION IF SCHEMA KEY DATA NOT AVAILABLE
# MAIN IDEA: divide into sections as dictionaries and iterate through data as lists
# processing of actual col data should be done in different program, this is only for reading raw data.