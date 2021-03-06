import sys
import os

# checking to see if python is running in a conda environment
if not os.path.exists(os.path.join(sys.prefix, 'conda-meta')):
    raise EnvironmentError('Install failed: not running in a conda environment')

# finding the correct directory for the install
directory = None
for i in sys.path:
    if 'lib/python3.8/site-packages' in i and 'site-packages/' not in i and '.local' not in i:
        directory = i
if directory is None:
    raise OSError('Install failed: install path not found')

# running install command
command = 'PYTHONUSERBASE={} pip install .'.format(directory)
print(command)
os.system(command)