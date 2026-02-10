import zipfile
import os

zip_path = r"C:\Users\Arav Kilak\Downloads\expense-categorisation-system.zip"

if not os.path.exists(zip_path):
    print(f"Error: Zip file not found at {zip_path}")
else:
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            with open("zip_contents.txt", "w") as f:
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith(('/', '\\')): continue
                    if '__pycache__' in file_info.filename: continue
                    f.write(f"{file_info.filename}\n")
            print("Zip contents written to zip_contents.txt")
    except zipfile.BadZipFile:
        print("Error: Bad zip file")
    except Exception as e:
        print(f"Error inspecting zip: {e}")
