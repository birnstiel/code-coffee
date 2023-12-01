from mpi4py import MPI
import numpy as np

# MPI initialization
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
print('Python rank: ' + str(rank))

# Send integer to Fortran code
comm.Send([np.array([12489],dtype='i4'), MPI.INT], dest=1, tag=1)

# Receive double from Fortran code
num = np.array([0.],dtype='f8')
comm.Recv([num, MPI.DOUBLE], source=1, tag=2)
print('Python receives: ' + str(num))

# MPI Finalize
MPI.Finalize()
