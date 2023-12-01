from mpi4py import MPI
import numpy as np

# MPI initialization
comm = MPI.COMM_WORLD

# Send array to Fortran code
comm.Send([np.array([[10,11],[12,13]],dtype='i4'), MPI.INT], dest=1, tag=3)

# Send array to Fortran code
#comm.Send([np.array([[10,11],[12,13]],dtype='i4',order='F'), MPI.INT], dest=1, tag=3)

#arr[0][0] = 10
#arr[0][1] = 11
#arr[1][0] = 12
#arr[1][1] = 13

# MPI Finalize
MPI.Finalize()
