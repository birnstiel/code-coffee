#include <stdio.h>
#include <unistd.h>
#include <openacc.h>

/*************************************************/
/**  HOW TO COMPILE: nvc -acc test_openacc.c    **/
/*************************************************/

int main(){

  #pragma acc parallel   // Open a parallel region with OpenACC. Whatever is inside the brackets will be run on the GPU
  {
    if(acc_on_device(acc_device_default)){   // Function provided by OpenACC to check whether a code is being run on the GPU (the device)
      printf("Running on GPU\n");
    }else{
      printf("Running on CPU\n");
    }
  } // acc parallel

  sleep(10);  // Wait for 10 seconds, to check that nvidia-smi shows that a code is running on the GPU

  return 0;


}