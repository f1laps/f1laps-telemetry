import os
from os import path

os_path = os.path.dirname(os.path.abspath(__file__))
path_to_dat = path.abspath(path.join(path.dirname(__file__), 'file.dat'))

print(path_to_dat)
