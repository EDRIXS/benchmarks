import argparse
import csv
import traceback


def main():
    parser = argparse.ArgumentParser(description="Time the edrixs MPI benchmark cases.")
    parser.add_argument("--nd", type=int, default=8,
                        help="nd value for the benchmark cases (default: 8)")
    parser.add_argument("--output", default="timings.csv", metavar="PATH",
                        help="CSV output file (default: timings.csv; overwritten)")
    args = parser.parse_args()

    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    output = None
    try:
        import edrixs
        from calculations import model, ed, xas, rixsmap, rixsmap_recompute, singlerixs

        # Compile the shared Numba operator kernels on every rank before timing.
        problem, _, _ = model(9)
        warmup_ops = edrixs.get_ops(*problem, backend="scipy", use_numba=True)
        del warmup_ops, problem
        comm.Barrier()

        if comm.rank == 0:
            output = open(args.output, "w", newline="")
            writer = csv.writer(output)
            writer.writerow(["function", "nd", "backend", "ranks", "seconds"])
            output.flush()
            print(f"{'function':<17} {'nd':>2} {'backend':<8} {'ranks':>5} {'seconds':>12}",
                  flush=True)

        nd = args.nd
        for backend in ["petsc", "fortran"]:
            for f in [ed, xas, singlerixs]:
                case_kws = {}
                if backend == "petsc" and f in (xas, singlerixs):
                    case_kws["matrix_lifetime"] = "recompute"
                comm.Barrier()
                start = MPI.Wtime()
                result = f(nd, backend=backend, **case_kws)
                elapsed = MPI.Wtime() - start
                del result
                seconds = comm.reduce(elapsed, op=MPI.MAX, root=0)
                if comm.rank == 0:
                    writer.writerow([f.__name__, nd, backend, comm.size, seconds])
                    output.flush()
                    print(f"{f.__name__:<17} {nd:>2} {backend:<8} "
                          f"{comm.size:>5} {seconds:>12.6f}", flush=True)
        if output is not None:
            output.close()
    except (Exception, KeyboardInterrupt):
        traceback.print_exc()
        comm.Abort(1)


if __name__ == "__main__":
    main()
