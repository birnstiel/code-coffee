# README

1. `python test_multiprocessing.py`

This creates a data set, and wants to process it. It uses `multiprocessing` to do so. When executed, we see that the data set is created, several times as each process tries to **import** it separately, which is always a call to creating it.

2. `mprof run --multiprocess test_multiprocessing.py && mprof plot`

This shows that each thread has the same memory consumption. This is not desired at all.

3. `python test_multiprocessing.py` but with `multiprocess` instead of `multiprocessing`

This shows that all IDs and also the arrays are the same. Only required change is removing the `ing` from `multiprocessing`.

4. `python test_shared.py` is slightly more involved but also more general: first a shared memory array is created that other parts of the code can access by name. `mprof run --multiprocess test_sharing.py && mprof plot` shows basically the same behavior as in 3.
