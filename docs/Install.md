# Installation Instructions

#### Installing
It is recommended that you  download the MAGNA-U
    package directly from Github at [https://github.com/sammysiegel/MAGNA-U](https://github.com/sammysiegel/MAGNA-U). This is easy
   to do on the command line. Just go to the directory you wish to download to and do:
   
```bash
git init
git clone https://github.com/sammysiegel/MAGNA-U
```

If you are running in an Anaconda environment, you can use the `install.py` script that
comes with MAGNA-U to easily install to the right place. Simply run:

```bash
cd MAGNA-U
python install.py
```

This will install MAGNA-U to a location like `/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages`.
If you are not in an Anaconda environment, you can run a command like this:

```bash
cd MAGNA-U
PYTHONUSERBASE=/path/to/install/location pip install .
```

You can check what the correct path is by running in Python:
```python
import sys
print(sys.path)
```

This will give you a list of places which will work to put the package.

You can test to see whether MAGNA-U is working by running in the MAGNA-U directory:

```python
python testthis.py
```
   
Once it is installed you can import using:
```python
import magna.utils as mu
```
   
#### Updating

To update MAGNA-U, first go to the MAGNA-U directory you cloned from Github. From there, just 
pull the update and reinstall:

```bash
git pull
python install.py
```

#### Dependencies

MAGNA-U requires an environment with Python 3.8. It also requires Ubermag to be
installed in your environment. Specifically, the following packages currently
must be available in your environment in order to work:

 - `ast, csv, random, time, os` from Python Standard Library
 - `numpy`, `pandas`, and `scipy`
 - `discretisedfield`, `micromagneticmodel`, and `oommfc` from Ubermag
 - `matplotlib` and `k3d` for plotting
 - `opencv-python` (import as `cv2`) 
 - `networkx` for constructing graphs