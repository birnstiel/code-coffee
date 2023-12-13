import h5py

# Open file in read-mode
h5file = h5py.File('newfile.h5', 'r')
print("These are the keys of the file: \n", h5file.keys())

# We can I am assigning a pointer to the dataset, not actual fetching data
h5dset = h5file['group1']['dataset1']
print("This is what I read in: \n", h5dset)
print("Shape of the dataset: \n", h5dset.shape)
print("Type of the dataset: \n", h5dset.dtype)

# When I am slicing I am reading to memory the data
print("Reading in some values... \n", h5dset[20:22, 2])

h5file.close()
