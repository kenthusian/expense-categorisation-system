import zipfile
import os

zip_path = r"C:\Users\Arav Kilak\Downloads\expense-categorisation-system.zip"
extract_to = "merge_source"

files_to_extract = [
    "expense-categorisation-system/app.py",
    "expense-categorisation-system/src/financial_health.py",
    "expense-categorisation-system/src/goals.py",
    "expense-categorisation-system/src/model.py",
    "expense-categorisation-system/src/data_processor.py"
]

if not os.path.exists(extract_to):
    os.makedirs(extract_to)

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in files_to_extract:
            try:
                # Extract to merge_source, flattening structure slightly? 
                # No, let's keep structure to avoid confusion, or just extract specific files.
                zip_ref.extract(file, extract_to)
                print(f"Extracted {file}")
            except KeyError:
                print(f"File not found in zip: {file}")
except Exception as e:
    print(f"Error: {e}")
