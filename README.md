## Run These Commands First:

> python -m venv .venv

> .\\.venv\Scripts\activate

frozen dependencies from requirements, OR:

> python -m pip install --upgrade --no-cache-dir -U pip --prefer-binary

> python -m pip install --no-cache-dir -U PyPDF2 --prefer-binary

> python -m pip install --no-cache-dir -U pandas --prefer-binary

## Project Structure:

- .venv
  -> create virtual environment with [python -m venv .venv] to keep packages local
- JSON-output
  -> guid-ed json output files will be here, can be more organized in further updates
- PDF-input
  -> place pdfs here, any file with \*.pdf in this folder will be processed, stick to ASCII naming
- src
- .gitignore
- .python-version
  -> use pyenv to trigger local version of python, HIGHLY RECOMMEND
- README.md

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

## Notes:

TODO: TRIGGERS EXCEPTION IF SCHEMA KEY DATA NOT AVAILABLE
MAIN IDEA: divide into sections as dictionaries and iterate through data as lists
processing of actual col data should be done in different program, this is only for reading raw data.
