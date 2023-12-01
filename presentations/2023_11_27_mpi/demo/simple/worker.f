      use mpi
      use omp_lib
      implicit none
      
      integer ierr,var,comm,rank,i
      real*8 num
! MPI initialization
      call MPI_INIT(ierr)
      comm = MPI_COMM_WORLD
      call MPI_COMM_RANK(comm, rank, ierr)
      write(*,*) 'Fortran rank: ',rank
      
! Receive integer from Python code and print it
      call MPI_RECV(var,1,MPI_INT,0,1,comm,MPI_STATUS_IGNORE,ierr)
      write(*,*) 'Fortran receives: ',var
      
! Send double to Python code
      num = 3.d6
      call MPI_SEND(num,1,MPI_DOUBLE_PRECISION,0,2,comm,ierr)
      
! OpenMP in Fortran code
      call omp_set_num_threads(4)
!$OMP PARALLEL DO
      do i=1,4
         write(*,*) 'Fortran OpenMP: ',i
      enddo
!$OMP END PARALLEL DO

! MPI Finalize
      call MPI_FINALIZE(ierr)
      return
      end
