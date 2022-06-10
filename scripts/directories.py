import os
from pathlib import Path

project_name = 'Cuenca'
if not os.path.isdir(project_name):
    os.makedirs(project_name, exist_ok=True)

sub_directories = ['/shps','/rst','/model','/json','/vtk']

directories = [Path(project_name+folder) for folder in sub_directories]
for workspace in directories:
    workspace.mkdir(exist_ok=True)