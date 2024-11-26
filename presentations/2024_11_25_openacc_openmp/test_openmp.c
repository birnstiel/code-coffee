#include <stdio.h>
#include <unistd.h>
#include <omp.h>

/***************************************************/
/**  HOW TO COMPILE: nvc -mp=gpu test_openmp.c    **/
/***************************************************/

int main(){

  #pragma omp target // Open a parallel region with OpenMP. Whatever is inside the brackets will be run on the GPU
  {
    if(!omp_is_initial_device()){ // Function provided by OpenMP to check whether a code is being run on the GPU or on the CPU (the "initial_device")
      printf("Running on GPU\n");
    }else{
      printf("Running on CPU\n");
    }
  } // omp target
  
  sleep(10);  // Wait for 10 seconds, to check that nvidia-smi shows that a code is running on the GPU
  
  return 0;
}
