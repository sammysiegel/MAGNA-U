# Pre-Generating Mesh CSV Files
A mesh csv file lists all the points in a mesh for a particular MNP assembly geometry, plus whether each point is in a core, shell, or outside of an MNP for each point in the mesh.

Here are the steps for pre-generating mesh csv files:

### Before use

If you have pulled MAGNA-U from Github, take a look at the file `MAGNA-U/mesh_making/genmesh1.slurm`. You'll see that the `srun` command links to Sammy's installation of Python and Sammy's version of `makethecsvs.py`. If you want to change this, you'll want to alter the command so that it looks like:
```bash
srun [path to your python] [path to your makethecsvs.py] $SLURM_ARRAY_TASK_ID $1
```

### Step 1 - Specify the mesh parameters
Go to your MAGNA-U installation and open the file `MAGNA-U/mesh_making/makethecsvs.py`. On line 9, you should see a line of code defining the variable `mnp` as an instance of the `MNP` class. You can change the attributes of that [`MNP`](MNP.md) to what you want. So your line should look like:
```python
mnp = mu.MNP({the attributes you want})
```
You should make sure specify values for  `r_tuple`, `discretizations`, `form`, `n_layers`, and `layer_radius`, as these will determine the mesh.

### Step 2 - Run slurm jobs in parallel
Running the slurm jobs in parallel will greatly reduce the time required to generate the mesh csv file by dividing up the mesh into sublists and handling each one as separate jobs.

You'll need to choose how many jobs to split the mesh up into. This will probably depend on how much of a rush you're in and how full the queue is. Let's call the number of jobs you choose `N` to make the next instruction easier to follow:

In the `MAGNA-U/mesh_making` folder, run the following command:
```bash
sbatch --array=0-{N-1} genmesh1.slurm N
```
Note that in the array tag, you should go up to the number of jobs - 1, whereas in the argument following the filename, you should put the number of jobs.

### Step 3 - Wait for the jobs to finish
In the `MAGNA-U/mesh_making` folder, each job should produce a csv once it has finished name `{job_number}.csv`.

### Step 4 - Combine the csvs to produce the final file
Once all jobs have finished, run the following command in the `MAGNA-U/mesh_making` folder:
```bash
python genmesh2.py {N} {filename to save to}
```
The first argument is the number of jobs that were run, and the second argument is the filename that you wish to save the complete mesh csv file to.

### Step 5 - Use it!
You can easily use a pre-generated mesh csv in your MAGNA-U runs by passing the location of the mesh as a parameter when definining your `MNP` object. Just pass the argument `mesh_csv = {location of csv file}`. Make sure that the file you generated matches the dimensions of the MNP you are trying to create, otherwise you might get weird results and/or errors!
