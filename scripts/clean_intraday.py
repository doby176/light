#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import datetime as dtmod

import pandas as pd


TIMESTAMP_CANDIDATES: List[str] = [
    "timestamp",
    "time",
    "datetime",
    "date",
    "dt",
    "Datetime",
    "Timestamp",
    "Time",
]


def detect_time_column(columns: List[str], user_time_col: Optional[str]) -> Optional[str]:
    if user_time_col and user_time_col in columns:
        return user_time_col
    lower_map = {c.lower(): c for c in columns}
    for cand in TIMESTAMP_CANDIDATES:
        if cand in columns:
            return cand
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def parse_and_convert_timezone(series: pd.Series, input_tz: Optional[str], to_tz: str) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce", utc=False)
    # Localize or convert
    try:
        if getattr(dt.dt, "tz", None) is not None:
            dt_local = dt.dt.tz_convert(to_tz)
        else:
            # If input_tz is None, assume timestamps are already in to_tz
            tz_from = to_tz if input_tz is None else input_tz
            dt_local = dt.dt.tz_localize(tz_from).dt.tz_convert(to_tz)
    except Exception:
        # Fallback: treat as naive in target tz
        dt_local = dt
    return dt_local


def filter_regular_session(dt_eastern: pd.Series) -> pd.Series:
    # Keep 09:30 to 15:59 inclusive (minute bars labeled at minute start)
    times = dt_eastern.dt.time
    start_t = dtmod.time(9, 30)
    end_t = dtmod.time(15, 59)
    return (times >= start_t) & (times <= end_t)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean intraday data: convert to US/Eastern, keep 09:30–16:00 session, sort & dedupe.")
    parser.add_argument("--in", dest="in_path", required=True, help="Input CSV path")
    parser.add_argument("--out", dest="out_path", required=False, help="Output CSV path (default: *_RTH.csv)")
    parser.add_argument("--time-col", dest="time_col", default=None, help="Timestamp column name (auto-detect if omitted)")
    parser.add_argument("--input-tz", dest="input_tz", default=None, help="Input timezone (e.g., America/New_York). If omitted, assumes timestamps are already in target tz")
    parser.add_argument("--to-tz", dest="to_tz", default="America/New_York", help="Target timezone for output (default: America/New_York)")
    parser.add_argument("--sep", dest="sep", default=",", help="CSV separator (default ',')")
    parser.add_argument("--parquet", action="store_true", help="Also write a Parquet copy next to output CSV")

    args = parser.parse_args()

    in_path = Path(args.in_path)
    if not in_path.exists():
        print(f"Input not found: {in_path}", file=sys.stderr)
        sys.exit(1)

    # Load CSV (attempt autodetect if sep not provided)
    try:
        if args.sep == ",":
            df = pd.read_csv(in_path, sep=None, engine="python")
        else:
            df = pd.read_csv(in_path, sep=args.sep)
    except Exception as e:
        print(f"Failed to read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    orig_rows = df.shape[0]

    # Detect timestamp column
    time_col = detect_time_column(list(df.columns), args.time_col)
    if time_col is None:
        print("Could not detect a timestamp column. Pass --time-col.", file=sys.stderr)
        sys.exit(1)

    # Parse and convert tz -> Eastern
    dt_local = parse_and_convert_timezone(df[time_col], args.input_tz, args.to_tz)

    # Filter to RTH 09:30–16:00 (keeping 09:30..15:59)
    mask = filter_regular_session(dt_local)
    kept = int(mask.sum())

    # Prepare output DataFrame
    df_out = df.loc[mask].copy()

    # Overwrite timestamp column with naive Eastern (no tz) for CSV friendliness
    df_out[time_col] = dt_local.loc[mask].dt.tz_localize(None)

    # Sort and drop duplicate timestamps
    df_out.sort_values(time_col, inplace=True)
    before_dedup = df_out.shape[0]
    df_out.drop_duplicates(subset=[time_col], keep="first", inplace=True)
    deduped = before_dedup - df_out.shape[0]

    # Determine output path
    if args.out_path:
        out_csv = Path(args.out_path)
    else:
        out_csv = in_path.with_name(in_path.stem + "_RTH.csv")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(out_csv, index=False)

    # Optional Parquet
    if args.parquet:
        out_parquet = out_csv.with_suffix(".parquet")
        try:
            df_out.to_parquet(out_parquet, index=False)
        except Exception as e:
            print(f"Parquet write failed (install pyarrow or fastparquet): {e}", file=sys.stderr)

    # Summary
    days = df_out[time_col].dt.date.unique()
    print("Clean complete:")
    print(f"- input rows: {orig_rows:,}")
    print(f"- kept RTH rows: {kept:,}")
    print(f"- removed as non-RTH: {orig_rows - kept:,}")
    print(f"- removed duplicates: {deduped:,}")
    print(f"- output rows: {df_out.shape[0]:,}")
    print(f"- output CSV: {out_csv}")
    if args.parquet:
        print(f"- output Parquet: {out_parquet}")


if __name__ == "__main__":
    main()