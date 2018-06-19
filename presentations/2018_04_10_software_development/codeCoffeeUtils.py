import numpy as np
from scipy.integrate import quad

def importantFunction(x, y, lum):
    # here should be some comment what that formula is...
    rvalue = 10**((y-(2.4**2.+((lum-x)/0.78)**2)**0.5-1.5*lum)) 
    return rvalue

def luminosity_function(Luminosity_bin, Luminosity_bin_width, y2, x2, gamma, z_clus, z_pivot):    
    # create a bin array
    Luminosity_bin =    np.array(Luminosity_bin, ndmin=1,dtype=np.float)
    
    # make sure we have floats    
    y2    = float(y2)
    x2    = float(x2)
    gamma = float(gamma)
    
    # generate the upper border
    Luminosity_bin_up    =    Luminosity_bin + Luminosity_bin_width

    # some computations
    phi_low =  importantFunction(x2, y2, Luminosity_bin) 
    phi_up  =  importantFunction(x2, y2, Luminosity_bin_up)
    phi     = (phi_low+phi_up)/2.
    phi     = phi * ((1.+z_clus)/(1.+z_pivot))**gamma

    # return the main value
    return phi 

def numGalaxies_probDist(Lmin, Lmax, Luminosity_bin_width, y1, x1, gamma, redshift, Mass):
    """
    This function calculates the total number of galaxies (LF_integ) and CDF (probab_distribution)
    """
    probab_distribution      = []
    luminosity_bins_for_prob = []

    # integrate over the luminosity function
    luminosity_bins = np.arange(Lmin, Lmax, Luminosity_bin_width)
    LF_integ         = quad(lambda luminosity_bins : luminosity_function(luminosity_bins, Luminosity_bin_width, y1, x1, gamma, redshift, 0.46), luminosity_bins[0], luminosity_bins[len(luminosity_bins)-1])[0] * Mass

    # Building a probability distribution function
    luminosity_bins_11 = np.linspace(Lmin, luminosity_bins[len(luminosity_bins)/5], 25) #np.linspace(Lmin, Lmax, 25)
    luminosity_bins_12 = np.linspace(luminosity_bins[len(luminosity_bins)/5], Lmax, 25)[1:]
    luminosity_bins_1  = np.append(luminosity_bins_11, luminosity_bins_12)

    for i in range (0, len(luminosity_bins_1)):
        probab_i        =    quad(lambda luminosity_bins : luminosity_function(luminosity_bins, Luminosity_bin_width, y1, x1, gamma, redshift, 0.46), luminosity_bins_1[0], luminosity_bins_1[i])[0] * Mass / LF_integ
        probab_distribution.append(probab_i)
        luminosity_bins_for_prob.append(luminosity_bins_1[i])

    return LF_integ, probab_distribution, luminosity_bins_for_prob

def writeArraytoFile(mass1, mass2, z1, z2, theArray):
    # form the file name
    # string formatting in python-2.x: https://docs.python.org/2/library/string.html#format-string-syntax
    # string formatting in python-3.x: https://docs.python.org/3/library/string.html#format-string-syntax
    fileName = 'myoutput_%sp%s_z%sp%s.npy' % (str(mass1), str(mass2), str(z1), str(z2))

    # write the array to file
    np.save(fileName, theArray)

def readIteratorData(infile):
    # load the input data
    sampler_cleaned = np.loadtxt(infile)

    burnin = 20000
    sampler_cleaned = np.array(sampler_cleaned[burnin:])
    y2 = sampler_cleaned[:,0]
    x2 = sampler_cleaned[:,1]
    g2 = sampler_cleaned[:,2]
    #    Apply some cuts here to avoid a very large number of AGN population in the cluster, as an example for y2=32, the number of AGNs are very large!
    iid = np.random.randint(len(y2), size=1000)
    y1  = y2[iid]
    x1  = x2[iid]
    g1  = g2[iid]

    return x1, y1, g1