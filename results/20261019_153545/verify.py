import csv, math, re, sys
from pathlib import Path
p = Path(sys.argv[1])
errors = []
status = (p / 'status.log').read_text()
for nd in range(8, 1, -1):
    try:
        assert re.search(rf'^nd={nd} exit=0 ', status, re.M), 'unsuccessful exit'
        with (p / f'timings_nd{nd}.csv').open() as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == ['function', 'nd', 'backend', 'ranks', 'seconds'], 'wrong CSV header'
            rows = list(reader)
        assert len(rows) == 6, f'{len(rows)} rows'
        assert {r['backend'] for r in rows} == {'petsc', 'fortran'}, 'wrong backends'
        assert {(r['function'], r['backend']) for r in rows} == {(f, b) for f in ('ed', 'xas', 'singlerixs') for b in ('petsc', 'fortran')}, 'wrong cases'
        for r in rows:
            assert r['function'] in {'ed', 'xas', 'singlerixs'} and int(r['nd']) == nd and int(r['ranks']) == 2, 'wrong case'
            assert math.isfinite(float(r['seconds'])) and float(r['seconds']) >= 0, 'invalid timing'
        print(f'nd={nd}: exit=0, 6 valid timings, 2 ranks')
    except Exception as e:
        errors.append(f'nd={nd}: {e}')
if (p / 'source_before.sha256').read_bytes() != (p / 'source_after.sha256').read_bytes():
    errors.append('Source files changed during execution')
else:
    print('Source files unchanged.')
inhibitors = (p / 'inhibitors.log').read_text()
if not any('long calculation' in line and 'sleep' in line and 'idle' in line and 'handle-lid-switch' in line for line in inhibitors.splitlines()):
    errors.append('Requested inhibitor not verified')
else:
    print('Sleep/idle/lid-switch inhibitor verified during execution.')
if errors:
    print('FAILURES:')
    print('\n'.join(errors))
    sys.exit(1)
print('Total: 7 successful runs, 42 valid timing rows.')
