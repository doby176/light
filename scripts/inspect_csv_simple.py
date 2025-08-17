# C:\Users\ASUS\scripts\inspect_csv_simple.py

import pandas as pd
import numpy as np
from pathlib import Path

# Change this to your local CSV path if different
FILE_PATH = Path(r"C:\Users\ASUS\qqq_10yr_1min.csv")

TIMESTAMP_CANDIDATES = [
    "timestamp", "time", "datetime", "date", "dt",
    "Datetime", "Timestamp", "Time",
]
OPEN_CANDIDATES = ["open", "Open", "OPEN"]
HIGH_CANDIDATES = ["high", "High", "HIGH"]
LOW_CANDIDATES = ["low", "Low", "LOW"]
CLOSE_CANDIDATES = ["close", "Close", "CLOSE", "adj_close", "Adj Close", "Adj_Close"]
VOLUME_CANDIDATES = ["volume", "Volume", "VOL", "Vol"]


def find_col(cols, candidates):
    lower_map = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand in cols:
            return cand
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def main():
    if not FILE_PATH.exists():
        print(f"File not found: {FILE_PATH}")
        return

    # Try to auto-detect CSV delimiter
    df = pd.read_csv(FILE_PATH, sep=None, engine="python")

    print("\n=== Data Shape ===")
    print(f"rows: {len(df):,}, cols: {df.shape[1]}")

    print("\n=== Columns & Dtypes ===")
    for c in df.columns:
        nn = int(df[c].notna().sum())
        na = int(df[c].isna().sum())
        print(f"- {c}: dtype={df[c].dtype}, non_null={nn}, nulls={na}")

    # Time analysis (basic)
    tcol = find_col(list(df.columns), TIMESTAMP_CANDIDATES)
    if tcol:
        dt = pd.to_datetime(df[tcol], errors="coerce", utc=False)
        print("\n=== Time Analysis (basic) ===")
        print(f"time_column: {tcol}")
        print(f"parsed_non_null: {int(dt.notna().sum()):,} / {len(dt):,}")
        if dt.notna().any():
            dts = dt.dropna().sort_values()
            print(f"min: {dts.iloc[0]}")
            print(f"max: {dts.iloc[-1]}")
            print(f"unique_timestamps: {dts.nunique():,}")
            print(f"duplicate_timestamps: {int(dts.duplicated().sum()):,}")
            days = dts.dt.date
            per_day = pd.Series(days).value_counts()
            if not per_day.empty:
                print("per_day_counts_summary:", {
                    "min": int(per_day.min()),
                    "p10": int(np.percentile(per_day, 10)),
                    "median": int(np.median(per_day)),
                    "p90": int(np.percentile(per_day, 90)),
                    "max": int(per_day.max()),
                })
    else:
        print("\n=== Time Analysis ===")
        print("No timestamp-like column found (try names like Timestamp, Datetime, time).")

    # OHLC sanity (basic)
    o = find_col(list(df.columns), OPEN_CANDIDATES)
    h = find_col(list(df.columns), HIGH_CANDIDATES)
    l = find_col(list(df.columns), LOW_CANDIDATES)
    c = find_col(list(df.columns), CLOSE_CANDIDATES)
    v = find_col(list(df.columns), VOLUME_CANDIDATES)

    print("\n=== OHLC Sanity (basic) ===")
    print({"open": o, "high": h, "low": l, "close": c, "volume": v})
    if all(col is not None and col in df.columns for col in [o, h, l, c]):
        bad_low = int((df[l] > df[[o, h, c]].min(axis=1)).sum())
        bad_high = int((df[h] < df[[o, l, c]].max(axis=1)).sum())
        non_pos = int(((df[[o, h, l, c]] <= 0).any(axis=1)).sum())
        print("violations:", {
            "low_greater_than_min_ohlc": bad_low,
            "high_less_than_max_ohlc": bad_high,
            "non_positive_ohlc_rows": non_pos,
        })
        rng = (df[h] - df[l]).clip(lower=0)
        if np.issubdtype(rng.dtype, np.number):
            rng_non_null = rng.dropna()
            if not rng_non_null.empty:
                print("range_summary_cents:", {
                    "mean": float(rng_non_null.mean() * 100),
                    "p95": float(np.percentile(rng_non_null, 95) * 100),
                    "max": float(rng_non_null.max() * 100),
                })
    if v and v in df.columns:
        print("volume_issues:", {
            "negative_volume_rows": int((df[v] < 0).sum()),
            "zero_volume_rows": int((df[v] == 0).sum()),
        })

    print("\n=== Sample Head (5) ===")
    print(df.head(5))

    print("\n=== Sample Tail (5) ===")
    print(df.tail(5))


if __name__ == "__main__":
    main()