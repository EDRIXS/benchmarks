#!/usr/bin/bash
set -u
cd /home/mdean/Documents/programs/benchmarks
run_dir="$(cd "$(dirname "$0")" && pwd)"
export TZ=America/New_York
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PATH=/home/mdean/miniconda3/envs/edrixs_env_petsc/bin:$PATH
{
date --iso-8601=seconds
command -v python mpirun
python --version
mpirun --version
printenv OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS
} > "$run_dir/environment.log" 2>&1
systemd-inhibit --list --no-pager > "$run_dir/inhibitors.log" 2>&1
sha256sum tasks.py calculations.py > "$run_dir/source_before.sha256"
for nd in 8 7 6 5 4 3 2; do
  printf 'nd=%s started=%s\n' "$nd" "$(date --iso-8601=seconds)" >> "$run_dir/status.log"
  mpirun -n 2 python tasks.py --nd "$nd" --output "$run_dir/timings_nd${nd}.csv" > "$run_dir/nd${nd}.log" 2>&1
  result_code=$?
  printf 'nd=%s exit=%s finished=%s\n' "$nd" "$result_code" "$(date --iso-8601=seconds)" >> "$run_dir/status.log"
done
sha256sum tasks.py calculations.py > "$run_dir/source_after.sha256"
python "$run_dir/verify.py" "$run_dir" > "$run_dir/verification.log" 2>&1

verification_code=$?
python "$run_dir/compare.py" "$run_dir" > "$run_dir/comparison.log" 2>&1
exit "$verification_code"
