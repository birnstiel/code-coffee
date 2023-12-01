Requirement:
OpenMPI, mpi4py for parent.py

Compilation:
mpifort -o worker -fopenmp worker.f

Execution:
mpiexec -n 1 python parent.py : -n 1 worker
