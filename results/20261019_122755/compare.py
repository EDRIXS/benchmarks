import csv, sys
from pathlib import Path
p = Path(sys.argv[1])
old = p.parent / '20261019_114916'
with (p / 'comparison.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['nd', 'backend', 'previous_seconds', 'current_seconds', 'speedup'])
    for nd in range(8, 1, -1):
        try:
            with (old / f'timings_nd{nd}.csv').open() as src:
                before = {r['backend']: float(r['seconds']) for r in csv.DictReader(src)}
            with (p / f'timings_nd{nd}.csv').open() as src:
                after = {r['backend']: float(r['seconds']) for r in csv.DictReader(src)}
            for backend in ['petsc', 'fortran']:
                a, b = before[backend], after[backend]
                speedup = a / b if b else float('inf')
                writer.writerow([nd, backend, a, b, speedup])
                print(f'nd={nd} {backend}: {a:.3f}s -> {b:.3f}s; speedup={speedup:.3f}x')
        except Exception as e:
            print(f'nd={nd}: comparison unavailable: {e}')
print('Single observations per case; timing validation does not establish numerical equivalence.')
