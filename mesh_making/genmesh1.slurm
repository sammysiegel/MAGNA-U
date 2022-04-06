#!/usr/bin/bash

##SBATCH --partition=48core
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --job-name=genmesh1
#SBATCH --time=8-23:59:59

## change the paths below to your paths
srun /home/students/ssiegel/anaconda3/envs/ubermag/bin/python3.8 /home/students/ssiegel/ubermag/MAGNA-U/mesh_making/makethecsvs.py $SLURM_ARRAY_TASK_ID $1