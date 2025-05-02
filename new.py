import os
import re
import xlrd
import openpyxl
from datetime import datetime
from openpyxl.cell.cell import Cell
import pandas as pd

# Main folder path
main_folder_path = r"D:\RIghtstroken\Pricing\PricingExtraction\Pricing_Sheets_24-Feb-25"
output_file = "final_summary_all_folders.xlsx"

# Field patterns
patterns = {
    "Part# / Model name": r"(part\s*#|model\s*name)",
    "OPP#": r"opp\s*#?",
    "CUSTOMER": r"\b(customer|customer name|client|client name)\b",
    "Assembly cost / PPD": r"\b(assembly cost|ppd)\b",
    "Estimated BOM cost": r"\b(estimated bom cost|bom cost per unit)\b",
    "Design & Development cost": r"design and development cost",
    "Recommended Price": r"recommended price",
    "Comments to Steven": r"(comments for steven\.s|comments to steven)",
    "CREATED ON": r"created\s*on\s*[:\-]?"
}

# Clean extracted values
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
            for fmt in ["%d-%b-%y", "%d-%b-%Y"]:
                try:
                    return datetime.strptime(match.group(0), fmt).strftime("%m/%d/%Y")
                except:
                    continue
    return str(value).strip()

# XLS extractor
def extract_from_xls(sheet):
    extracted = {}
    for row_idx in range(sheet.nrows):
        for col_idx in range(sheet.ncols):
            cell_value = str(sheet.cell_value(row_idx, col_idx)).strip().lower()
            for key, pattern in patterns.items():
                if re.search(pattern, cell_value, re.IGNORECASE):
                    if key not in extracted:
                        next_value = ""
                        try:
                            if col_idx + 1 < sheet.ncols:
                                next_value = sheet.cell_value(row_idx, col_idx + 1)
                            if (not next_value or str(next_value).strip() == "") and row_idx + 1 < sheet.nrows:
                                next_value = sheet.cell_value(row_idx + 1, col_idx)
                            if (not next_value or str(next_value).strip() == "") and row_idx + 1 < sheet.nrows and col_idx + 1 < sheet.ncols:
                                next_value = sheet.cell_value(row_idx + 1, col_idx + 1)
                        except:
                            continue
                        extracted[key] = clean_value(next_value, key)
    return extracted

# XLSX extractor
def extract_from_xlsx(sheet):
    extracted = {}
    max_row = sheet.max_row
    max_col = sheet.max_column

    for row in sheet.iter_rows():
        for cell in row:
            if cell.value:
                value = str(cell.value).strip().lower()
                for key, pattern in patterns.items():
                    if re.search(pattern, value, re.IGNORECASE):
                        if key not in extracted:
                            next_val = None
                            try:
                                if cell.column + 1 <= max_col:
                                    next_val = sheet.cell(cell.row, cell.column + 1).value
                                if (not next_val or str(next_val).strip() == "") and cell.row + 1 <= max_row:
                                    next_val = sheet.cell(cell.row + 1, cell.column).value
                                if (not next_val or str(next_val).strip() == "") and cell.row + 1 <= max_row and cell.column + 1 <= max_col:
                                    next_val = sheet.cell(cell.row + 1, cell.column + 1).value
                            except:
                                continue
                            extracted[key] = clean_value(next_val, key, cell)
    return extracted

# Write to Excel with formatting
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    for subfolder in os.listdir(main_folder_path):
        subfolder_path = os.path.join(main_folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            data = []
            for filename in os.listdir(subfolder_path):
                if filename.endswith(".xls") or filename.endswith(".xlsx"):
                    file_path = os.path.join(subfolder_path, filename)
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
                        print(f"❌ Error reading {filename} in {subfolder}: {e}")
            if data:
                df = pd.DataFrame(data)
                sheet_name = subfolder[:31]
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                worksheet = writer.sheets[sheet_name]
                workbook = writer.book

                # Style for blank cells
                red_fill = workbook.add_format({
                    'bg_color': '#FF0000',
                    'font_color': '#FFFFFF',
                    'border': 1,
                    'align': 'left'
                })

                text_format = workbook.add_format({'num_format': '@'})

                for col_num, column in enumerate(df.columns):
                    worksheet.set_column(col_num, col_num, 25, text_format)
                    for row_num, cell_val in enumerate(df[column]):
                        if pd.isna(cell_val) or str(cell_val).strip() == "":
                            worksheet.write(row_num + 1, col_num, "Blank", red_fill)

print(f"✅ Final report generated: {output_file}")
