#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <openacc.h>

#define MAX_ITER 10000
#define MAX_PALETTE 100
#define f 1

static const int Nx = 1920 * f;
static const int Ny = 1080 * f;

int mandelbrot(int i, int j, int Nx, int Ny);
void write_to_file(int* M);

int main(int argc, char* argv[]){
    
    int* M = calloc (Nx * Ny, sizeof(int));

    //#pragma acc parallel loop                                                 // Use OpenACC to parallelize the for loops
    //#pragma omp target parallel for map(to: Nx, Ny) map(from: M[0: Nx*Ny])    // Use OpenMP  to parallelize the for loops 
    for(int j = 0; j < Ny; j++){
        for(int i = 0; i < Nx; i++){
            M[j * Nx + i] = mandelbrot(i, j, Nx, Ny) % MAX_PALETTE;
        }
    }

    //write_to_file(M);  // Comment out to just check the performances

    return 0;

}

int mandelbrot(int i, int j, int Nx, int Ny){
    static const double x_L = -1.7687784;
    static const double x_R = -1.7687792;
    static const double y_L = -0.0017386;
    static const double y_R = -0.0017392;

    double px = x_L + i * (x_R - x_L) / Nx;
    double py = y_L + j * (y_R - y_L) / Ny;

    double xc = px;
    double temp_xc = xc;
    double yc = py;
    short int iter = 0;
    while(xc*xc + yc*yc < 4 && iter < MAX_ITER){
        temp_xc = xc*xc - yc*yc + px;
        yc = 2.*xc*yc + py;
        xc = temp_xc;

        iter++;
    }
    return iter;
}


void write_to_file(int* M){
    FILE *file = fopen("matrix.txt", "w");
    for (int j = 0; j < Ny; j++) {
        for (int i = 0; i < Nx; i++) {
        
            fprintf(file, "%d ", M[j * Nx + i]);
        }
        fprintf(file, "\n");  // Newline after each row
    }
    fclose(file);
}


