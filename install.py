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

server = input('Are you installing onto a server? [y/n]')
if server=='y':
    with open('./magna/utils.py', 'a') as f:
        f.write("\n"*2)
        f.write("matplotlib.use('Agg')")

# running install command
command = 'PYTHONUSERBASE={} pip install .'.format(directory)
print(command)
os.system(command)

try:
    import cv2
except ModuleNotFoundError:
    print('\033[0;33;40mWARNING: MAGNA-U has detected that the python module OpenCV is not installed. This is needed'
          ' in order to make movies of hysteresis loops.')
    answer = input('Would you like to install OpenCV now? [y/n]\033[0;0m')
    if answer == 'y':
        os.system('pip install opencv-python')

try:
    import networkx
except ModuleNotFoundError:
    print('\033[0;33;40mWARNING: MAGNA-U has detected that the python module NetworkX is not installed. This is needed'
          ' in order to find the domains of MNP assemblies.')
    answer = input('Would you like to install NetworkX now? [y/n]\033[0;0m')
    if answer == 'y':
        os.system('pip install networkx')

