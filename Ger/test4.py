# pip install gerbonara
from gerbonara import read
import os

def load_and_print(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".gbr"):
            file_path = os.path.join(folder_path, file)
            print(f"\n📁 File: {file}")
            gerber = read(file_path)
            for cmd in gerber.commands:
                print(cmd)

load_and_print("path/to/your/gerber_folder")
