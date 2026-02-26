#!/usr/bin/env python3
import argparse
import numpy as np
from pathlib import Path

def parse_shells(s: str):
    return np.array([float(x) for x in s.split(",")], dtype=float)

def main():
    ap = argparse.ArgumentParser(
        description="Round FSL bvals to specified shells (e.g., 0,1500,3000)."
    )
    ap.add_argument("in_bval", help="input bvals file (FSL format)")
    ap.add_argument("out_bval", help="output rounded bvals file")
    ap.add_argument("--shells", default="0,1500,3000",
                    help='comma-separated shell values, default: "0,1500,3000"')
    ap.add_argument("--b0_thr", type=float, default=50.0,
                    help="values with |b| <= b0_thr are set to 0 (default: 50)")
    ap.add_argument("--max_dev", type=float, default=150.0,
                    help="warn if a non-b0 value is farther than this from nearest shell (default: 150)")
    args = ap.parse_args()

    shells = parse_shells(args.shells)
    in_path = Path(args.in_bval)
    vals = np.loadtxt(in_path, dtype=float)
    if vals.ndim != 1:
        vals = vals.ravel()

    rounded = np.empty_like(vals)

    # b0 handling
    b0_mask = np.abs(vals) <= args.b0_thr
    rounded[b0_mask] = 0.0

    # non-b0: nearest shell (excluding 0 shell for safety if provided)
    nonb = ~b0_mask
    shells_non0 = shells[shells != 0] if np.any(shells != 0) else shells
    diffs = np.abs(vals[nonb, None] - shells_non0[None, :])
    nearest_idx = np.argmin(diffs, axis=1)
    rounded_vals = shells_non0[nearest_idx]
    rounded[nonb] = rounded_vals

    # warnings
    max_dist = diffs[np.arange(diffs.shape[0]), nearest_idx]
    bad = max_dist > args.max_dev
    if np.any(bad):
        bad_idx = np.where(nonb)[0][bad]
        print("WARNING: Some b-values are far from any target shell.")
        for i in bad_idx[:20]:
            print(f"  index {i}: b={vals[i]:.1f} -> {rounded[i]:.1f} (dist={abs(vals[i]-rounded[i]):.1f})")
        if bad_idx.size > 20:
            print(f"  ... and {bad_idx.size-20} more")

    # write out (FSL bvals: single line)
    out_path = Path(args.out_bval)
    out_path.write_text(" ".join(str(int(round(x))) for x in rounded) + "\n")

    # summary
    def counts(x):
        uniq, cnt = np.unique(x.astype(int), return_counts=True)
        return dict(zip(uniq.tolist(), cnt.tolist()))

    print("Input shells (approx):", counts(vals))
    print("Rounded shells:", counts(rounded))

if __name__ == "__main__":
    main()
