      use mpi
      use omp_lib
      implicit none
      
      integer ierr,comm,i,j
      integer arr(2,2)
      real*8 num
! MPI initialization
      call MPI_INIT(ierr)
      comm = MPI_COMM_WORLD

! Receive array from Python code
      call MPI_RECV(arr,4,MPI_INT,0,3,comm,MPI_STATUS_IGNORE,ierr)
      do i=1,2
         do j=1,2
            write(*,*) arr(i,j)
         enddo
      enddo

! MPI Finalize
      call MPI_FINALIZE(ierr)
      return
      end
