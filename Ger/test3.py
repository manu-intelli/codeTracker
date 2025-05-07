# pip install gerber-parser


import os
from gerber_parser import GerberParser

def load_gerber(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".gbr"):
            file_path = os.path.join(folder_path, file)
            print(f"\n📁 {file}")
            parser = GerberParser(file_path)
            for cmd in parser:
                print(cmd)

load_gerber("path/to/your/gerber_folder")
