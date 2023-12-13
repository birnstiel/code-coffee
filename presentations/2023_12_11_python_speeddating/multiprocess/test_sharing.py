import time
import numpy as np
import multiprocessing
from multiprocessing import shared_memory

def set_up_shared_memory(N=300):

    # create a NumPy array
    arr = np.random.rand(N, N, N)
    print(f'shared array size: {arr.nbytes / (1024)**3:.3f} GB')

    # create the shared memory and give it a name
    shm = shared_memory.SharedMemory(
        create=True,
        size=arr.nbytes,
        name='my_shared_mem')

    # create a NumPy array backed by shared memory
    b = np.ndarray(
        arr.shape,
        dtype=arr.dtype,
        buffer=shm.buf)

    # Copy the original data into shared memory
    b[:] = arr[:]
    arr = b

def get_shared_array(N=300):

    # Open the existing shared memory
    shm = shared_memory.SharedMemory(name='my_shared_mem')

    # Load the array from shared memory
    shared_array = np.ndarray(
        shape=(N, N, N),
        dtype=np.float64,
        buffer=shm.buf)

    # to avoid garbage collection, we need to return both
    return shm, shared_array

def work(i):

    # Open the existing shared memory
    shm, arr = get_shared_array()

    # save the ID and value
    time.sleep(2)
    _id = id(arr.data)
    val = arr[0, 0, 0]

    # Close the shared memory
    shm.close()

    return _id, val


if __name__ == '__main__':

    set_up_shared_memory()

    p = multiprocessing.Pool(4)
    res = p.map(work, range(4))

    print([r[0] for r in res])
    print([r[1] for r in res])

    # get the array one last time to close it
    shm, arr = get_shared_array()
    shm.unlink()

    p.close()
