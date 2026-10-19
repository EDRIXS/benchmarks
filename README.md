# edrixs MPI benchmarks

Use a Python environment with edrixs (including its PETSc and Fortran backends),
numpy, matplotlib (imported by the calculations), and mpi4py. The MPI launcher
must match the MPI library used by that environment and the solver backends.

```sh
mpirun -n 8 python tasks.py
mpirun -n 8 python tasks.py --output timings-8.csv
mpirun -n 8 python tasks.py --nd 5 --output timings_nd5.csv
```

Run these commands from the `benchmarks` directory. The `--nd` option selects
the nominal impurity d-shell occupancy (0 through 9; default: 8) for every timed
case. The bath starts full, so the initial total valence occupancy is `nd + 10`.
Changing `nd` changes the basis size and computational cost; lower values do
not necessarily give smaller problems. `--output` defaults to `timings.csv`.

The runner executes the `petsc` backend followed by `fortran`, with functions
`ed`, `xas`, and `singlerixs` in that order for each backend.
The PETSc XAS and single-RIXS cases use `matrix_lifetime='recompute'` to rebuild
matrices between operations. Fortran uses its existing matrix handling. All ranks execute
each case together. Rank 0 prints one timing row per completed case and writes
`function,nd,backend,ranks,seconds` to the CSV. The output file is overwritten on
each run and flushed after each row, preserving completed measurements if a
later case fails. Python exceptions print a traceback and abort the MPI job.

Each time is the maximum elapsed time across ranks, measured with `MPI.Wtime()`
after a barrier. It includes the entire function call: model and operator
construction, solver work, and result preparation. It excludes imports, the
initial barrier, timing reduction, result disposal, and reporting. These are
single observations with no repetitions. Before timing, every rank builds
SciPy operators for `model(9)` to warm the shared Numba kernels, independently
of `--nd`. This does not warm the PETSc/SLEPc solvers; first-use backend imports
and initialization may still contribute to timings. The runs do not check numerical
agreement between backends. Solver output may also appear in the terminal.

For comparisons, keep the machine, software versions, process placement, rank
count, and thread settings consistent. For example, to use one thread per rank:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 mpirun -n 8 python tasks.py
```

Record those settings with your results; when comparing MPI scaling, vary only
the rank count. No additional benchmark or pytest plugins are required.

## Cleanup

After the benchmark has stopped, preview or remove edrixs working files:

```sh
python clean.py --dry-run
python clean.py
```

Cleanup targets the directory containing `clean.py`, including generated
`config.in`, operator and basis inputs, eigenvectors, and pole files. It preserves
timing CSVs and source files. The same edrixs files are excluded by `.gitignore`.
