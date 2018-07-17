/*
A simple CUDA C++ code to add 2 float arrays in different ways.
Stolen from https://devblogs.nvidia.com/even-easier-introduction-cuda/
K. Huber 2018
*/
#include <iostream>
#include <math.h>
#include <time.h>



// CUDA Kernel functions to add the elements of two arrays on the GPU

// one thread
__global__ void add_1(int n, float *x, float *y)
{
    for(int i = 0; i < n; i++)
      y[i] = x[i] + y[i];
}

// multiple threads in 1 block
__global__ void add_t(int n, float *x, float *y)
{
    int index = threadIdx.x;
    int stride = blockDim.x;
    for(int i = index; i < n; i+= stride)
      y[i] = x[i] + y[i];
}

// multiple blocks and threads
__global__ void add_bt(int n, float *x, float *y)
{
    int index = blockIdx.x * blockDim.x + threadIdx.x;
    int stride = blockDim.x * gridDim.x;
    for (int i = index; i < n; i += stride)
      y[i] = x[i] + y[i];
}

int main(void)
{
  time_t start_time, end_time;
  time(&start_time);
  int N = 1e7; // 10M elements

  // Allocate Unified Memory -- accessible from CPU or GPU
  float *x, *y;
  cudaMallocManaged(&x, N*sizeof(float));
  cudaMallocManaged(&y, N*sizeof(float));

  // initialize x and y arrays on the host
  for (int i = 0; i < N; i++) {
    x[i] = 1.0f;
    y[i] = 2.0f;
  }

  // Run kernel on the GPU
  //  add_1<<<1,1>>>(N,x,y);
  
//  add_t<<<1, 512>>>(N,x,y);

  int blockSize = 512;
  int numBlocks = (N + blockSize - 1) / blockSize;
  add_bt<<<numBlocks, blockSize>>>(N, x, y);

  // Wait for GPU to finish
  cudaDeviceSynchronize();

  // Check for errors (all values should be 3.0f)
  float maxError = 0.0f;
  for (int i = 0; i < N; i++)
    maxError = fmax(maxError, fabs(y[i]-3.0f));
  std::cout << "Max error: " << maxError << std::endl;

  // Free memory
  cudaFree(x);
  cudaFree(y);

  time(&end_time);
  std::cout << "time: " << difftime(end_time, start_time) << " s" << std::endl;

  return 0;
}

