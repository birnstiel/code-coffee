
/* example code for CTYPE calls from Python */
/* by Steffen Hagstotz 27/2/2018 			*/
/* hagstotz@usm.lmu.de 						*/

/* 
compile with 
mac: 	gcc-4.8 -dynamiclib -o clib.dylib clib.c -lgsl -lgslcblas -std=c99
linux: 	gcc-4.8 -shared -o clib.so -fPIC clib.c -lgsl -lm -std=c99 -lgslcblas
*/

/* --- includes --- */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include <gsl/gsl_math.h>
#include <gsl/gsl_integration.h>
#include <gsl/gsl_monte.h>
#include <gsl/gsl_monte_vegas.h>

#define NEVAL 1000 // number of gsl_integrate workspaces
#define epsrel 1e-5 // relative integration error for number counts

// angular diameter distance integrand
double aux_angular_distance(double z, void *params)
{
	double Omega_m = 0.27;
	double result;
	result = 1./sqrt(Omega_m * pow((1+z),3) + (1-Omega_m));
	return(result);
}

// angular diameter distance calculation
double angular_distance_c(double z)
{
	double result,error;
	gsl_integration_workspace *w = gsl_integration_workspace_alloc(NEVAL);
	gsl_function F;
	
	F.function = &aux_angular_distance;
	F.params = NULL;
	
	gsl_integration_qag(&F,0.0,z,0.0,epsrel,NEVAL,GSL_INTEG_GAUSS15,w,&result,&error);
	
	gsl_integration_workspace_free(w);

	result *= 3e5 * 1e-2 / (1.+z);

	return(result);
}

// integrand for monte carlo example integration
double aux_mc_integral (double *x, size_t dim, void *params)
{
  (void)(dim); /* avoid unused parameter warnings */
  (void)(params);
  double A = 1.0 / (M_PI * M_PI * M_PI);
  return A / (1.0 - cos (x[0]) * cos (x[1]) * cos (x[2]));
}

// monte carlo example integration
double mc_integral(void)
{
	double result, error;

	// integration boundaries
	double x_lower[3] = { 0, 0, 0 };
	double x_upper[3] = { M_PI, M_PI, M_PI };

	// GSL random number generator
	const gsl_rng_type *T;
	gsl_rng *r;

	// integrand, dimension, additional parameters
	gsl_monte_function G = { &aux_mc_integral, 3, 0 };

	// number of calls
	size_t calls = 100000;

	gsl_rng_env_setup ();

	T = gsl_rng_default;
	r = gsl_rng_alloc (T);

	gsl_monte_vegas_state *s = gsl_monte_vegas_alloc (3);

	gsl_monte_vegas_integrate (&G, x_lower, x_upper, 3, 10000, r, s,
	                       &result, &error);

	gsl_monte_vegas_integrate (&G, x_lower, x_upper, 3, calls, r, s,
	                           &result, &error);

	return(result);
}

// example function to read in an array from Python
int datain(double *pointer_to_data, int size_of_array)
{
	double result = 0;

	for (int i = 0; i < size_of_array; ++i)
	{
		result += pointer_to_data[i];
	}

	return(result);
}