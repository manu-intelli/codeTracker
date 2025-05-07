import os
from pcbtools import GerberFile

def load_all_gerber_files(folder_path):
    gerber_data = {}

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".gbr"):
            file_path = os.path.join(folder_path, filename)
            try:
                gerber = GerberFile.from_file(file_path)
                gerber_data[filename] = gerber
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    return gerber_data

def print_gerber_commands(gerber_data):
    for filename, gerber in gerber_data.items():
        print(f"\n📁 File: {filename}")
        for command in gerber.commands:
            print(command)

# Example usage
folder_path = "path/to/your/gerber_folder"  # Replace with your actual path
data = load_all_gerber_files(folder_path)
print_gerber_commands(data)
