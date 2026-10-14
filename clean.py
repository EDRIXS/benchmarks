#!/usr/bin/env python
"""Remove edrixs working files from the directory containing this script."""

import argparse
from pathlib import Path


PATTERNS = (
    "config.in",
    "hopping_i.in", "hopping_n.in",
    "coulomb_i.in", "coulomb_n.in",
    "fock_i.in", "fock_n.in", "fock_f.in",
    "transop_components.in", "transop_xas.in",
    "transop_rixs_i.in", "transop_rixs_f.in",
    "eigvals.dat", "denmat.dat",
    "eigvec.*", "xas_poles.*", "rixs_poles.*",
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="list matching files without deleting them")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    for pattern in PATTERNS:
        for path in sorted(root.glob(pattern)):
            if path.is_file() or path.is_symlink():
                if not args.dry_run:
                    path.unlink()
                print(f"{'Would remove' if args.dry_run else 'Removed'} {path.name}")


if __name__ == "__main__":
    main()
