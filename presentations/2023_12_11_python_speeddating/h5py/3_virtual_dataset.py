# The HDF5 Virtual Dataset (VDS) feature allows you to:
# - access data from a collection of HDF5 files as a single, unified dataset
# - without modifying how the data is stored in the original files
# - it can have unlimited dimensions and map to source datasets with unlimited
#   dimensions

import h5py
import numpy as np

# Create 1D data in 4 source files (0.h5 to 3.h5)
for n in range(4):
    with h5py.File(f"{n}.h5", "w") as src_file:
        src_file.create_dataset("data", (100,), "i4", np.arange(0, 100) + n)

# Make a 2D virtual layout - this is a special h5py object to help
# with creating virtual datasets.
layout = h5py.VirtualLayout(shape=(4, 100), dtype="i4")

# Map each source dataset into the layout
for n in range(4):
    vsource = h5py.VirtualSource(f"{n}.h5", "data", shape=(100,))
    # Both layout and source can be sliced like a dataset or an array
    # Here, we're mapping every second element (::2) from the source
    # into the first 50 cells of the row for this file.
    layout[n, :50] = vsource[::2]

# Finally, turn the layout into a dataset in a file
vds_file = h5py.File("VDS.h5", "w")
vds_file.create_virtual_dataset("vdata", layout, fillvalue=-5)
print(vds_file['vdata'][:, :5])
vds_file.close()
