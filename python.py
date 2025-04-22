import os
import re
import pandas as pd
import xlrd
import openpyxl

folder_path = "your_folder_path_here"  # Replace this with your actual folder path
output_file = "final_summary1.xlsx"

data = []

# Regex patterns
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
            cell_val = str(sheet.cell_value(row_idx, col_idx)).strip().lower()
            for key, pattern in patterns.items():
                if re.search(pattern, cell_val, re.IGNORECASE):
                    try:
                        raw_value = sheet.cell_value(row_idx, col_idx + 1)
                        cell_type = sheet.cell_type(row_idx, col_idx + 1)

                        # If it's a date, try to keep raw string format if possible
                        if key == "CREATED ON" and cell_type == xlrd.XL_CELL_DATE:
                            extracted[key] = sheet.cell(row_idx, col_idx + 1).value  # raw value
                        else:
                            extracted[key] = str(raw_value)
                    except:
                        continue
    return extracted

def extract_from_xlsx(sheet):
    extracted = {}
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value is not None:
                val = str(cell.value).strip().lower()
                for key, pattern in patterns.items():
                    if re.search(pattern, val, re.IGNORECASE):
                        try:
                            next_cell = sheet.cell(row=cell.row, column=cell.column + 1)
                            raw_value = next_cell.value
                            if raw_value is not None:
                                # Store raw value as string without formatting
                                extracted[key] = str(raw_value)
                        except:
                            continue
    return extracted

# Process files
for filename in os.listdir(folder_path):
    if filename.endswith(".xls") or filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)
        row_data = {"File Name": filename}

        try:
            if filename.endswith(".xls"):
                book = xlrd.open_workbook(file_path, formatting_info=False)
                sheet = book.sheet_by_index(0)
                extracted = extract_from_xls(sheet)
            else:
                wb = openpyxl.load_workbook(file_path, data_only=False)  # Don't apply formatting
                sheet = wb.active
                extracted = extract_from_xlsx(sheet)

            row_data.update(extracted)
            data.append(row_data)

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

# Export to Excel
df = pd.DataFrame(data)
df.to_excel(output_file, index=False)
print(f"✅ Summary saved to {output_file}")
