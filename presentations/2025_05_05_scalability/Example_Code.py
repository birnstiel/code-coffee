'''
@file Example_Code.py
@brief A Python3 script for calculating statistical distances using MPI for parallel processing.

This script uses MPI to distribute the computation of statistical distances between two datasets 
across multiple processes. It calculates histograms of distances and combines the results from 
all processes into a final histogram. It was created for a CodeCoffee session on strong and weak scaling.

@author Geray S. Karademir
@date 05/05/2025
'''

import sys
import numpy as np
from mpi4py import MPI
import matplotlib.pyplot as plt
from timeit import default_timer as timer

'''
@brief Calculate statistical distances and histograms.

This function computes the pairwise distances between points in two datasets and creates histograms 
of these distances for each point in the first dataset.

@param args A tuple containing:
    - Data1: The first dataset (array of shape (n, 2)).
    - Data2: The second dataset (array of shape (m, 2)).
    - bins: The histogram bins (array of shape (k,)).

@return A 1D array representing the summed histogram of distances.
'''
def get_statistical_distances(args):
    Data1, Data2, bins = args
    # Create return arrays
    dist = np.zeros((len(Data1), len(Data2)))
    dist_hist = np.zeros((len(Data1), len(bins)-1))

    # Calculate the distance between each point in Data1 and Data2
    # and create a histogram for each point in Data1
    for i in range(len(Data1)):
        dist = np.sqrt((Data1[i][0] - Data2[:,0])**2 + (Data1[i][1] - Data2[:,1])**2)
        dist_hist[i] = np.histogram(dist, bins=bins)[0]

    # Sum the histograms for each process
    dist_hist = np.sum(dist_hist,axis=0)
    return dist_hist

'''
@brief Scatter data across MPI processes.

This function distributes rows of the dataset `Data1` across all MPI processes.

@return A 2D array containing the portion of `Data1` assigned to the current process.
'''
def scatter_data(Data1):
    #Create arrays for variable sizes
    rows_per_rank = np.full(size, npart_data // size)
    rows_per_rank[:npart_data % size] += 1
    
    # Create a buffer for Data1 on each rank depending on the number of rows it will receive
    Data1_on_task = np.empty((rows_per_rank[rank], 2))

    # Calculate the displacements for the scatter operation
    displacements = np.cumsum(np.insert(rows_per_rank[:-1], 0, 0)) * 2  # *2 for the 2 columns
 
    # Scatter the data
    comm.Scatterv([Data1, rows_per_rank * 2, displacements, MPI.DOUBLE], Data1_on_task, root=0)
    return Data1_on_task

if __name__ == "__main__":
    '''
    @brief Main function to execute the MPI-based statistical distance calculation.

    This script performs the following steps:
    1. Initializes MPI and determines the rank and size of the processes.
    2. Creates random datasets and histogram bins on the root process.
    3. Broadcasts `Data2` and `bins` to all processes.
    4. Scatters `Data1` across all processes.
    5. Computes histograms of distances on each process.
    6. Gathers and combines the results into a final histogram on the root process.
    7. Plots and saves the final histogram as a PNG file.
    '''
    
    start = timer()
    start_serial_1 = timer()
    
    npart_data = int(sys.argv[1])
    Nbins = 20

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    # Create random data for Data1 and Data2 and bins
    # Only the root process creates the data
    if rank == 0:
        print(f"Running with {size} Processes")
        print(f"Running with {npart_data} x {npart_data} particles.")
        Data1 = np.random.rand(npart_data,2)
        Data2 = np.random.rand(npart_data,2)
        bins = np.linspace(0, 1.5, Nbins)
    else:
        Data1 = None
        Data2 = np.empty((npart_data,2))
        bins = np.empty(Nbins)
    
    end_serial_1 = timer()
    # Sync to make sure all processes are ready before broadcasting/scattering
    comm.Barrier()

    # Broadcast Data2 and bins to all processes
    comm.Bcast(Data2, root=0)
    comm.Bcast(bins, root=0)

    # Scatter Data1 to all processes
    Data1_on_task = scatter_data(Data1)

    # Now calc distance on each task
    dist_hist = get_statistical_distances([Data1_on_task, Data2, bins])

    # Create a buffer to gather the results
    dist_hist_fin = None
    if rank == 0:
        dist_hist_fin = np.empty([size, len(dist_hist)])

    # Gather results
    comm.Gather(dist_hist, dist_hist_fin, root=0)

    if rank == 0:
        start_serial_2 = timer()
        # Create final histogram
        # Sum the histograms from all processes
        dist_hist_fin = np.sum(dist_hist_fin, axis=0)

        # Plot the histogram
        plt.figure(figsize=(8, 6))
        plt.title('Statistical Distance Histogram')
        plt.xlabel('Distance')
        plt.ylabel('Frequency')
        plt.bar(bins[:-1], dist_hist_fin, width=np.diff(bins), align='edge', alpha=0.5)
        plt.savefig('MPI_histogram_'+str(size)+'.png')
        plt.close()
        
        end_serial_2 = timer()
        end = timer()
        
        part1  = end_serial_1 - start_serial_1
        part2  = end_serial_2 - start_serial_2
        
        # print('Serial part took', part1+part2, " sec")
        print('Calculation took', end-start, " sec")
        