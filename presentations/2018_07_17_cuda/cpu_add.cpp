/*
A simple C(++) code to add 2 float arrays; for comparison;
Stolen from https://devblogs.nvidia.com/even-easier-introduction-cuda/
K.Huber 2018
*/

#include <iostream>
#include <math.h>
#include <time.h>
// function/kernel to add the elements of two arrays
void add(int n, float *x, float *y)
{
  for (int i = 0; i < n; i++)
      y[i] = x[i] + y[i];
}

int main(void)
{
  time_t start_time, end_time;
  time(&start_time);
  int N = 1e7; // 10M elements

  float *x = new float[N];
  float *y = new float[N];

  // initialize x and y arrays on the host
  for (int i = 0; i < N; i++) {
    x[i] = 1.0f;
    y[i] = 2.0f;
  }

  // Run kernel on the CPU
  add(N, x, y);

  // Check for errors (all values should be 3.0f)
  float maxError = 0.0f;
  for (int i = 0; i < N; i++)
    maxError = fmax(maxError, fabs(y[i]-3.0f));
  std::cout << "Max error: " << maxError << std::endl;

  // Free memory
  delete [] x;
  delete [] y;

  time(&end_time);
  std::cout << "time:" << difftime(end_time, start_time) << " s" <<std::endl;

  return 0;
}

