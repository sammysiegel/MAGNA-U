import csv
import numpy as np
import sys
import os

batches = int(sys.argv[1])

filename = str(sys.argv[2])

full_array = np.empty((1,4))

np.savetxt(filename, full_array, delimiter=',')

for i in range(batches):
    arr = np.genfromtxt('{}.csv'.format(i), delimiter=',')
    full_array = np.concatenate((full_array, arr))

full_array = np.delete(full_array, 0, 0)

np.savetxt(filename, full_array, delimiter=',')

for i in range(batches):
    os.system('rm {}.csv'.format(i))
os.system('rm -r ./MNP_Data')
os.system('rm *.out')