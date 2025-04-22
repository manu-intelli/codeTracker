import os
import re
import xlrd
import openpyxl
import pandas as pd
from openpyxl.utils.datetime import from_excel

folder_path = "your_folder_path_here"  # Replace this
output_file = "final_summary1.xlsx"

data = []

patterns = {
    "Part# / Model name": r"(part\s*#|model\s*name)",
    "OPP#": r"opp\s*#?",
    "CUSTOMER": r"customer",
    "Assembly cost / PPD": r"\b(assembly cost|ppd)\b",
    "Estimated BOM cost": r"\b(estimated bom cost|bom cost per unit)\b",
    "Design & Development cost": r"design and development cost",
    "Recommended Price": r"recommended price",
    "Comments to Steven": r"(comments for steven\.s|comments to steven)",
    "CREATED ON": r"created\s*on\s*[:\-]?"
}

def extract_from_xls(sheet):
    extracted = {}
    for row_idx in range(sheet.nrows):
        for col_idx in range(sheet.ncols):
            cell_value = str(sheet.cell_value(row_idx, col_idx)).strip().lower()
            for key, pattern in patterns.items():
                if re.search(pattern, cell_value, re.IGNORECASE):
                    try:
                        next_cell = sheet.cell_value(row_idx, col_idx + 1)
                        if key not in extracted:
                            # For .xls, dates come as float if date-formatted
                            if isinstance(next_cell, float) and 'date' in key.lower():
                                extracted[key] = xlrd.xldate.xldate_as_datetime(next_cell, sheet.book.datemode).strftime("%m/%d/%Y")
                            else:
                                extracted[key] = str(next_cell)
                    except:
                        continue
    return extracted

def extract_from_xlsx(sheet):
    extracted = {}
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value is not None:
                value = str(cell.value).strip().lower()
                for key, pattern in patterns.items():
                    if re.search(pattern, value, re.IGNORECASE):
                        try:
                            next_cell = sheet.cell(cell.row, cell.column + 1)
                            val = next_cell.value
                            if key not in extracted:
                                if isinstance(val, float) and "date" in next_cell.number_format.lower():
                                    # Convert Excel serial to readable date
                                    extracted[key] = from_excel(val).strftime("%m/%d/%Y")
                                else:
                                    extracted[key] = str(val)
                        except:
                            continue
    return extracted

# Process each Excel file
for filename in os.listdir(folder_path):
    if filename.endswith(".xls") or filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)
        row_data = {"File Name": filename}

        try:
            if filename.endswith(".xls"):
                book = xlrd.open_workbook(file_path)
                sheet = book.sheet_by_index(0)
                extracted = extract_from_xls(sheet)
            else:
                wb = openpyxl.load_workbook(file_path, data_only=True)
                sheet = wb.active
                extracted = extract_from_xlsx(sheet)

            row_data.update(extracted)
            data.append(row_data)

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

# Save to Excel
df = pd.DataFrame(data)
df.to_excel(output_file, index=False)
print(f"✅ Summary saved to {output_file}")
