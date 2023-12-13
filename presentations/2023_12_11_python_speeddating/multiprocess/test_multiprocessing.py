import numpy as np
import time
import multiprocess as mp

# create some data

N = 300
arr = np.random.rand(N, N, N)
print(f'module array size: {arr.nbytes / (1024)**3:.3f} GB')


def work(i):
    time.sleep(2)
    # return the ID and the first element of the array
    return id(arr.data), arr[0, 0, 0]


if __name__ == '__main__':

    p = mp.Pool(4)
    res = p.map(work, range(4))
    p.close()

    print([r[0] for r in res])
    print([r[1] for r in res])
