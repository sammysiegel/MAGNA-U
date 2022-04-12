import magna.utils as mu
import sys
import numpy as np

run = int(sys.argv[1])

batches = int(sys.argv[2])

mnp = mu.MNP(run,
             r_tuple=(5.0e-9, 3.8e-9, 3.8e-9),
             discretizations = (7, 7, 7), 
             form = 'fcc',
             layer_radius = 7, 
             n_layers = 11)
### ^^^^^^ Replace the line above MNP you want to generate a mesh for. The r_tuple, discretizations, 
###        form, n_layers, and layer_radius should all be specific to your MNP setup.

mesh_list = list(mnp.mesh)

subsize = (len(mesh_list)//batches) + 1

sublist = mesh_list[subsize*run:subsize*(run+1)]

arrayz=[]
for point in sublist:
    arrayz.append(list(point) + [mnp.if_coreshell(point)])

np.savetxt('{}.csv'.format(run), np.array(arrayz), delimiter=',')