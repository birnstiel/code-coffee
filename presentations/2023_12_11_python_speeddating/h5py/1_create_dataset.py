import numpy as np
import h5py

h5file = h5py.File('newfile.h5', 'w', swmr=True)

h5group = h5file.create_group('group1')

h5dset = h5group.create_dataset(name='dataset1',
                                shape=(300, 20), dtype=np.uint8, chunks=True,
                                compression='gzip', shuffle=True)

# You can add meta-data to your datasets
h5dset.attrs['title'] = "Dataset from the third round of experiments"
h5dset.attrs['code_version'] = 2.1

h5dset[20:25, 2] = [5, 4, 3, 2, 1]
h5file.close()
