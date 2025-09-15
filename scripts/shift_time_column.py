#!/usr/bin/env python3
"""
Shift the first column (time in hours) of a CSV by a fixed offset (default +14h).

Usage:
  python3 shift_time_column.py <input_csv> [--offset 14] [--no-mod]

Notes:
  - Assumes the first row is a header and keeps it unchanged.
  - Applies modulo 24 by default (so values wrap around a 24h clock).
  - Writes a new file next to input: <name>_shifted+<offset>.csv
"""

import argparse
import csv
import os
from decimal import Decimal, InvalidOperation, getcontext


def shift_time(value: str, offset: Decimal, use_mod: bool) -> str:
    # Increase precision to avoid visible rounding artifacts
    getcontext().prec = 28
    try:
        t = Decimal(value)
    except InvalidOperation:
        # If cannot parse, return original
        return value
    t = t + offset
    if use_mod:
        # modulo 24 while maintaining sign/Decimal behavior
        twenty_four = Decimal(24)
        t = t % twenty_four
    # Normalize to remove exponent formatting but keep decimals
    return format(t.normalize(), 'f')


def main():
    parser = argparse.ArgumentParser(description="Shift CSV time column by fixed hours")
    parser.add_argument("input_csv", help="Path to input CSV")
    parser.add_argument("--offset", type=Decimal, default=Decimal(14), help="Hours to add to time column (default 14)")
    parser.add_argument("--no-mod", action="store_true", help="Do not apply modulo 24 wrap-around")
    args = parser.parse_args()

    inp = args.input_csv
    base, ext = os.path.splitext(inp)
    outp = f"{base}_shifted+{args.offset}{ext or '.csv'}"

    use_mod = not args.no_mod

    with open(inp, newline='') as f_in, open(outp, 'w', newline='') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)

        first = True
        for row in reader:
            if not row:
                writer.writerow(row)
                continue
            if first:
                # header
                writer.writerow(row)
                first = False
                continue
            row[0] = shift_time(row[0], args.offset, use_mod)
            writer.writerow(row)

    print(outp)


if __name__ == "__main__":
    main()
