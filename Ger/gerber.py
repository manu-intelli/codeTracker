import os
import openpyxl
from pygerber.gerberx3.api.v2 import GerberFile

# Function to read the content of a Gerber file as text
def read_gerber_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Function to compare two Gerber files at a detailed content level
def compare_gerber_files_detailed(file1, file2):
    # Read and compare the contents of the files
    content1 = read_gerber_file(file1)
    content2 = read_gerber_file(file2)

    if content1 == content2:
        return True, "No difference"
    else:
        # Find differences: Let's highlight the first few differences for illustration
        diff_lines = []
        file1_lines = content1.splitlines()
        file2_lines = content2.splitlines()

        # Compare line by line
        for i, (line1, line2) in enumerate(zip(file1_lines, file2_lines)):
            if line1 != line2:
                diff_lines.append(f"Line {i+1}:\nFile 1: {line1}\nFile 2: {line2}\n")

        return False, "\n".join(diff_lines)

# Function to compare all Gerber files in two directories
def compare_folders(folder1, folder2):
    # Get the list of Gerber files in both folders
    files_folder1 = [f for f in os.listdir(folder1) if f.endswith('.GBR')]
    files_folder2 = [f for f in os.listdir(folder2) if f.endswith('.GBR')]

    # Results container
    comparison_results = []

    for file1 in files_folder1:
        file1_path = os.path.join(folder1, file1)
        file2_path = os.path.join(folder2, file1)

        # If the file exists in both folders, compare them
        if file1 in files_folder2:
            is_identical, diff_info = compare_gerber_files_detailed(file1_path, file2_path)
            comparison_results.append({
                'file': file1,
                'identical': is_identical,
                'deviation': "No deviation" if is_identical else f"Deviations found:\n{diff_info}"
            })
        else:
            comparison_results.append({
                'file': file1,
                'identical': False,
                'deviation': "File missing in second folder"
            })

    return comparison_results

# Function to export results to Excel
def export_to_excel(results, output_file):
    # Create a new workbook and set up the sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Gerber File Comparison"
    
    # Set headers
    ws.append(["File Name", "Identical", "Deviation"])

    # Add data rows
    for result in results:
        ws.append([result['file'], "Yes" if result['identical'] else "No", result['deviation']])

    # Save the workbook
    wb.save(output_file)

# Specify your folder paths
folder_after = r'D:\Rightstroke Project\Gerber\After_ACX_GBR'
folder_before = r'D:\Rightstroke Project\Gerber\Before_ACX_GBR'

# Compare the files in the two folders
results = compare_folders(folder_after, folder_before)

# Output file path for the Excel sheet
output_excel_file = r'D:\Rightstroke Project\Gerber\Gerber_Comparison_Result.xlsx'

# Export the comparison results to Excel
export_to_excel(results, output_excel_file)

print(f"Comparison complete! Results saved to {output_excel_file}")
