# Installation Instructions

#### Installing
It is recommended that you  download the MAGNA-U
    package directly from Github at [https://github.com/sammysiegel/MAGNA-U](https://github.com/sammysiegel/MAGNA-U). This is easy
   to do on the command line. Just go to the directory you wish to download to and do:
   ```bash
   git init
   git clone https://github.com/sammysiegel/MAGNA-U
   ```
   Additionally, it is pretty easy to install
    the package with pip so you can make it available in your environment without
   having to worry about whether it is in your working directory or not. You just need to
   find the right path. If you are using an Anaconda environment, that will look
   something like `/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages`.
   Once you have downloaded the MAGNA-U repository from Github, do the following:
   ```bash
   cd MAGNA-U
   PYTHONUSERBASE=/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages pip install .
   ```
   
    If this doesn't work you can check what the correct path is by running in Python:
    ```python
    import sys
    print(sys.path)
    ```
    This will give you a list of places which will work to put the package.
   
   Once it is installed you can import using:
    ```python
    import magna.utils as mu
    ```
   
#### Updating

To update MAGNA-U, first go to the MAGNA-U directory you cloned from Github. From there, just run:
```shell
git pull
```

Then, just re-run the pip command you used to install MAGNA-U:
```shell
PYTHONUSERBASE=/[path_to_anaconda]/envs/[env_name]/lib/python3.8/site-packages pip install .
```

#### Dependencies

MAGNA-U requires an environment with Python 3.8. It also requires Ubermag to be
installed in your environment. Specifically, the following packages currently
must be available in your environment in order to work:
 - `ast, csv, random, time, os` from Python Standard Library
 - `numpy`
 - `discretisedfield`, `micromagneticmodel`, and `oommfc` from Ubermag
 - `matplotlib` and `k3d` for plotting
