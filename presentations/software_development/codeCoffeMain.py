# from the python libraries
import sys
import argparse
from math import *

# other important libraries
import numpy as np
from scipy.interpolate import interp1d

# some of my personal general libraries
sys.path.insert(0, '/home/mkuemmel/workspace/CodeCoffee')
import Cosmology
import HaloConcentration
import HaloDensityProfile

# libraries next to main
import cosmolopy.distance as cd
import Martin_Cosmology as mc
import codeCoffeeUtils

def defineSpecificProgramOptions():
    """
    @brief Allows to define the (command line and configuration file) options
    specific to this program
    
    @details
        See the Elements documentation for more details.
    @return
        An  ArgumentParser.
    """
    # general setup of the parser
    description="""
    An example program for the Code Coffee. Well, I could now write much much 
    more. But I dont really know what the program is supposed to be doing, so
    it is better to leave it at that!
    """
    parser = argparse.ArgumentParser(prog='test.py', description=description)

    # add the mandatory parameters
    parser.add_argument("-m1", "--mass1", metavar="mass1", type=float, help="lower mass limit", required=True)
    parser.add_argument("-m2", "--mass2", metavar="mass2", type=float, help="upper mass limit", required=True)
    parser.add_argument("-z1", "--redshift1", metavar="z1", type=float, help="lower redshift limit", required=True)
    parser.add_argument("-z2", "--redshift2", metavar="z2", type=float, help="upper limit limit", required=True)

    # add the parameters that have defaults
    parser.add_argument("-l1", "--lmin", metavar="lmin", type=float, default=23.0,
                        help="lower luminosity limit [default: %(default)s]", required=False)
    parser.add_argument("-l2", "--lmax", metavar="lmax", type=float, default=21.0,
                        help="upper luminosity limit [default: %(default)s]", required=False)
    parser.add_argument("-i", "--indata", metavar="indata", type=str, default='mydata.txt',
                        help="file with the input data [default: %(default)s]", required=False)

    # return the arguments
    return parser.parse_args()

def main():
    # some constants
    Om_M = 0.314
    Om_L = 1.-Om_M
    H0   = 67.4

    # get all arguments
    allArgs = defineSpecificProgramOptions()

    # cluster parameters
    Mass     = 10**(allArgs.mass1 + allArgs.mass2/10.)
    redshift = allArgs.z1 + allArgs.z2/10.
    
    # distance Measurements and K-correction
    dist_ang    = mc.Angular_diameter_distance (redshift,  Om_M,   Om_L,  H0)
    dist_lum    = dist_ang * (1.+ redshift)**2.
    alpha       = 0.7
    Kcorrection = (1.+ redshift)**alpha / (1.+ redshift)
    
    # to change K100y to T200z of clusters using Hanny & Nanny (2015)
    params                =    {'flat': True, 'H0': H0, 'Om0': Om_M, 'Ob0': 0.049, 'sigma8': 0.83, 'ns': 0.96}
    Cosmology.addCosmology('myCosmo', params)
    M200c, R200c, c200c   =    HaloDensityProfile.changeMassDefinitionCModel (Mass * H0 / 100., redshift, '500c', '200c')        #    Input M500 M_solar h^-1 and output as M200 M_solar h^-1 and R200c in Kpc h^-1
    
    # compute M200c and R200c
    M200c = M200c / H0 * 100.
    R200c = R200c * 1.e-3 / H0 * 100.

    # get the arrays to iterate over from the file
    x1, y1, g1 = codeCoffeeUtils.readIteratorData(allArgs.indata)

    Luminosity_bin_width    = 0.001
    degree_of_contamination = []
    for jj in range(1000):
        LF_integ, probab_distribution, luminosity_bins_for_prob = codeCoffeeUtils.numGalaxies_probDist(allArgs.lmin, allArgs.lmax, Luminosity_bin_width, y1[jj], x1[jj], g1[jj], redshift, Mass)
        #--------------------------------------------------------------------------------------------
        #    Get the degree of contamination s = Total KKD Flux / SZE flux, for different clusters of same mass and at same redshift
        #--------------------------------------------------------------------------------------------
        probab_distribution_interp    =    interp1d(probab_distribution, luminosity_bins_for_prob, kind='nearest')
    
        # generate random numbers from the Poisson's distribution with mean equivalent to the number of sources (LF_integ) calculated from the Luminosity function with that mass and redshift and then get a uniform number between 0 and 1 to get the AGN luminosity using LF as the probability distribution function    
        random_sample            = np.array([ np.random.uniform(0, 1., size = np.random.poisson(LF_integ)) for n in xrange(100000) ])     # where we assume a redshift evolution in the AGNs with gamma = 2.5
        Total_AGN_luminosity     = np.array([ np.sum( 10.0**probab_distribution_interp(ssample) ) for ssample in  random_sample ])
        Total_AGN_flux           = np.array(Total_AGN_luminosity / ( dist_lum**2. * (3.08*1.e22)**2. * 4. *pi * 1.e-29 *Kcorrection))
        degree_of_contamination1 = Total_AGN_flux#-Total_AGN_flux/SZE_flux200
        degree_of_contamination.extend(degree_of_contamination1)
        del probab_distribution
        del luminosity_bins_for_prob
        degree_of_contamination1 = []
        random_sample = []

    # write out the array to file        
    codeCoffeeUtils.writeArraytoFile(allArgs.mass1, allArgs.mass2, allArgs.z1, allArgs.z2, np.array(degree_of_contamination))

if __name__ == '__main__':
    main()