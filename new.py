from pathlib import Path
import pandas as pd
import re
import xlrd
from openpyxl import load_workbook
from openpyxl.cell import Cell
from datetime import datetime

# Define field patterns
patterns = {
    "PROJECT CODE": r"(project\s*code|code\s*project|project\s*id|job\s*code)",
    "CUSTOMER": r"(customer|client|buyer)",
    "VEHICLE NO": r"(vehicle\s*no|vehicle\s*number|truck\s*no|lorry\s*no|reg\s*no)",
    "DESCRIPTION": r"(description|item\s*desc|details)",
    "CREATED ON": r"(created\s*on|date|issued\s*on|generated\s*on)"
}

# Clean and standardize value
def clean_value(value, key, cell=None):
    if isinstance(cell, Cell) and cell.is_date:
        return cell.value.strftime("%m/%d/%Y")
    if isinstance(value, float) and key == "CREATED ON":
        try:
            date_value = datetime(*xlrd.xldate_as_tuple(value, 0))
            return date_value.strftime("%m/%d/%Y")
        except:
            pass
    if isinstance(value, str) and key == "CREATED ON":
        match = re.search(r"(\d{1,2})[-/\s](\w{3,})[-/\s](\d{2,4})", value, re.IGNORECASE)
        if match:
            for fmt in ["%d-%b-%y", "%d-%b-%Y", "%d/%b/%y", "%d/%b/%Y"]:
                try:
                    return datetime.strptime(match.group(0), fmt).strftime("%m/%d/%Y")
                except:
                    continue
    return str(value).strip()

# Extract data from .xls files
def extract_from_xls(sheet):
    extracted = {}
    for row_idx in range(sheet.nrows):
        for col_idx in range(sheet.ncols):
            cell_value = str(sheet.cell_value(row_idx, col_idx)).strip().lower()
            for key, pattern in patterns.items():
                if re.search(pattern, cell_value, re.IGNORECASE):
                    if key not in extracted:
                        candidate = sheet.cell_value(row_idx, col_idx)
                        if key == "CREATED ON" and re.search(r"\d{1,2}[-/\s]\w+[-/\s]\d{2,4}", str(candidate), re.IGNORECASE):
                            extracted[key] = clean_value(candidate, key)
                        else:
                            next_value = ""
                            try:
                                next_value = sheet.cell_value(row_idx, col_idx + 1)
                                if not next_value or str(next_value).strip() == "":
                                    next_value = sheet.cell_value(row_idx + 1, col_idx)
                                if not next_value or str(next_value).strip() == "":
                                    next_value = sheet.cell_value(row_idx + 1, col_idx + 1)
                            except:
                                continue
                            extracted[key] = clean_value(next_value, key)
    return extracted

# Extract data from .xlsx files
def extract_from_xlsx(sheet):
    extracted = {}
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value:
                value = str(cell.value).strip().lower()
                for key, pattern in patterns.items():
                    if re.search(pattern, value, re.IGNORECASE):
                        if key not in extracted:
                            candidate = value
                            if key == "CREATED ON" and re.search(r"\d{1,2}[-/\s]\w+[-/\s]\d{2,4}", candidate, re.IGNORECASE):
                                extracted[key] = clean_value(candidate, key, cell)
                            else:
                                next_val = None
                                try:
                                    next_val = sheet.cell(cell.row, cell.column + 1).value
                                    if not next_val or str(next_val).strip() == "":
                                        next_val = sheet.cell(cell.row + 1, cell.column).value
                                    if not next_val or str(next_val).strip() == "":
                                        next_val = sheet.cell(cell.row + 1, cell.column + 1).value
                                except:
                                    continue
                                extracted[key] = clean_value(next_val, key, cell)
    return extracted

# Main function
def process_excels(root_folder):
    data = []
    for path in Path(root_folder).rglob("*.*"):
        if path.suffix in [".xls", ".xlsx"]:
            try:
                if path.suffix == ".xls":
                    book = xlrd.open_workbook(path)
                    sheet = book.sheet_by_index(0)
                    extracted = extract_from_xls(sheet)
                else:
                    book = load_workbook(path, data_only=True)
                    sheet = book.active
                    extracted = extract_from_xlsx(sheet)
                extracted["FILE"] = str(path.name)
                data.append(extracted)
            except Exception as e:
                print(f"Error processing {path.name}: {e}")

    df = pd.DataFrame(data)
    df.to_excel("extracted_data.xlsx", index=False)
    print("Extraction completed and saved to extracted_data.xlsx")

# Call the main function with your root folder
# process_excels("your/folder/path/here")

