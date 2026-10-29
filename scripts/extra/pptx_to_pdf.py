# requirements
# sudo apt install unoconv
# pip install tqdm
# pip install glob
import glob
import os

import tqdm

path = "documents"
files = [f for f in glob.glob(path + "**/*.pptx", recursive=True)]
for f in tqdm.tqdm(files):
    command = f'unoconv -f pdf "{f}"'
    os.system(command)


## WELL TESTED FOR UBUNTU , WORKS PERFECTLY
