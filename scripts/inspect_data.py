#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


TIMESTAMP_CANDIDATES = [
    "timestamp",
    "time",
    "datetime",
    "date",
    "dt",
    "Datetime",
    "Timestamp",
    "Time",
]

OPEN_CANDIDATES = ["open", "Open", "OPEN"]
HIGH_CANDIDATES = ["high", "High", "HIGH"]
LOW_CANDIDATES = ["low", "Low", "LOW"]
CLOSE_CANDIDATES = ["close", "Close", "CLOSE", "adj_close", "Adj Close", "Adj_Close"]
VOLUME_CANDIDATES = ["volume", "Volume", "VOL", "Vol"]


def find_first_present(columns: List[str], candidates: List[str]) -> Optional[str]:
    for cand in candidates:
        if cand in columns:
            return cand
    # try case-insensitive
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def detect_time_column(columns: List[str], user_time_col: Optional[str]) -> Optional[str]:
    if user_time_col and user_time_col in columns:
        return user_time_col
    return find_first_present(columns, TIMESTAMP_CANDIDATES)


def read_excel_meta(file_path: Path) -> Tuple[List[str], Optional[pd.DataFrame]]:
    try:
        xl = pd.ExcelFile(file_path, engine="openpyxl")
        return xl.sheet_names, None
    except Exception as e:
        print(f"Error reading Excel metadata: {e}", file=sys.stderr)
        return [], None


def load_data(file_path: Path, sheet: Optional[str], sep: str) -> pd.DataFrame:
    suffix = file_path.suffix.lower()
    try:
        if suffix in [".xlsx", ".xls", ".xlsm"]:
            return pd.read_excel(file_path, sheet_name=sheet, engine="openpyxl")
        elif suffix in [".csv", ".txt"]:
            return pd.read_csv(file_path, sep=sep)
        elif suffix in [".parquet"]:
            return pd.read_parquet(file_path)
        else:
            # Fallback: try CSV then Excel
            try:
                return pd.read_csv(file_path, sep=sep)
            except Exception:
                return pd.read_excel(file_path, sheet_name=sheet, engine="openpyxl")
    except Exception as e:
        print(f"Error reading data: {e}", file=sys.stderr)
        raise


def parse_datetime(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce", utc=False)
    return dt


def localize_or_convert_timezone(dt: pd.Series, tz: Optional[str]) -> pd.Series:
    # If dt is timezone-aware, convert; else localize
    if tz is None:
        return dt
    try:
        if getattr(dt.dt, "tz", None) is not None:
            return dt.dt.tz_convert(tz)
        else:
            return dt.dt.tz_localize(tz)
    except Exception:
        # Fallback: return as-is if localization fails
        return dt


def summarize_dataframe(df: pd.DataFrame) -> Dict:
    nulls = df.isna().sum()
    dtypes = df.dtypes.astype(str)
    summary = {}
    for col in df.columns:
        info = {
            "dtype": dtypes[col],
            "non_null": int(df.shape[0] - nulls[col]),
            "nulls": int(nulls[col]),
        }
        if np.issubdtype(df[col].dtype, np.number):
            desc = df[col].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
            info["stats"] = {k: (float(v) if pd.notna(v) else None) for k, v in desc.items()}
        summary[col] = info
    return summary


def minute_regularities(dt: pd.Series) -> Dict:
    report: Dict[str, object] = {}
    if dt.isna().all():
        return {"error": "All timestamps are NaT after parsing."}

    # Sort and dedup for checks
    dt_sorted = dt.sort_values()
    duplicates = int(dt_sorted.duplicated().sum())
    report["total_rows"] = int(dt.shape[0])
    report["unique_timestamps"] = int(dt.nunique(dropna=True))
    report["duplicate_timestamps"] = duplicates

    # Basic coverage
    tmin, tmax = dt_sorted.iloc[0], dt_sorted.iloc[-1]
    if pd.isna(tmin) or pd.isna(tmax):
        report["error"] = "Timestamp min/max is NaT; check parsing."
        return report

    report["time_min"] = str(tmin)
    report["time_max"] = str(tmax)
    days = dt_sorted.dt.date
    unique_days = pd.Series(days.unique()).sort_values()
    report["unique_days"] = int(unique_days.shape[0])

    # Expected per-day minutes for regular session (approx): 390
    per_day_counts = dt_sorted.groupby(days).size()
    report["per_day_counts_summary"] = {
        "min": int(per_day_counts.min()),
        "p10": int(np.percentile(per_day_counts, 10)),
        "median": int(np.median(per_day_counts)),
        "p90": int(np.percentile(per_day_counts, 90)),
        "max": int(per_day_counts.max()),
    }
    days_full = int((per_day_counts >= 390).sum())
    days_half = int(((per_day_counts > 0) & (per_day_counts < 390)).sum())
    report["num_days_with_>=390_minutes"] = days_full
    report["num_days_with_<390_minutes"] = days_half

    # Minute gap check: build expected range per day and count missing
    # This assumes timestamps are aligned to minute boundaries
    missing_total = 0
    sample_gaps: List[Dict[str, object]] = []
    for day, cnt in per_day_counts.items():
        day_mask = days == day
        day_times = dt_sorted[day_mask]
        if day_times.empty:
            continue
        # Round to minute
        rounded = day_times.dt.floor("T")
        diffs = rounded.diff().dropna().dt.total_seconds() // 60
        # Gaps > 1 minute
        big_gaps = diffs[diffs > 1]
        if not big_gaps.empty:
            missing_here = int(((big_gaps - 1).sum()))
            missing_total += missing_here
            if len(sample_gaps) < 5:
                sample_gaps.append({
                    "day": str(day),
                    "first_gap_at": str(rounded.iloc[big_gaps.index[0]]),
                    "gap_minutes": int(big_gaps.iloc[0]),
                })
    report["approx_missing_minutes"] = int(missing_total)
    report["sample_gaps"] = sample_gaps

    return report


def ohlc_sanity(df: pd.DataFrame, col_map: Dict[str, Optional[str]]) -> Dict:
    report: Dict[str, object] = {}
    o, h, l, c = (
        col_map.get("open"),
        col_map.get("high"),
        col_map.get("low"),
        col_map.get("close"),
    )
    v = col_map.get("volume")

    present = {k: (col_map.get(k) is not None) for k in ["open", "high", "low", "close", "volume"]}
    report["present_columns"] = present

    if all(col is not None for col in [o, h, l, c]):
        # Basic inequalities
        bad_low = (df[l] > df[[o, h, c]].min(axis=1)).sum()
        bad_high = (df[h] < df[[o, l, c]].max(axis=1)).sum()
        non_positive = ((df[[o, h, l, c]] <= 0).any(axis=1)).sum()
        report["violations"] = {
            "low_greater_than_min_ohlc": int(bad_low),
            "high_less_than_max_ohlc": int(bad_high),
            "non_positive_ohlc_rows": int(non_positive),
        }
        # Ranges
        rng = (df[h] - df[l]).clip(lower=0)
        report["range_summary"] = {
            "mean_cents": float(rng.mean() * 100),
            "p95_cents": float(np.percentile(rng, 95) * 100),
            "max_cents": float(rng.max() * 100),
        }
    if v is not None and v in df.columns:
        neg_vol = (df[v] < 0).sum()
        zeros = (df[v] == 0).sum()
        report["volume_issues"] = {
            "negative_volume_rows": int(neg_vol),
            "zero_volume_rows": int(zeros),
        }
    return report


def normalize_column_map(columns: List[str]) -> Dict[str, Optional[str]]:
    return {
        "open": find_first_present(columns, OPEN_CANDIDATES),
        "high": find_first_present(columns, HIGH_CANDIDATES),
        "low": find_first_present(columns, LOW_CANDIDATES),
        "close": find_first_present(columns, CLOSE_CANDIDATES),
        "volume": find_first_present(columns, VOLUME_CANDIDATES),
    }


def generate_report(df: pd.DataFrame, time_col: Optional[str], tz: Optional[str]) -> Dict:
    report: Dict[str, object] = {}
    report["shape"] = list(df.shape)
    report["columns"] = list(df.columns)
    report["schema"] = summarize_dataframe(df)

    if time_col and time_col in df.columns:
        dt = parse_datetime(df[time_col])
        dt = localize_or_convert_timezone(dt, tz)
        report["time_column"] = time_col
        report["time_analysis"] = minute_regularities(dt)
    else:
        report["time_column"] = None
        report["time_analysis"] = {"note": "No time column detected. Pass --time-col to specify."}

    col_map = normalize_column_map(list(df.columns))
    report["ohlc_sanity"] = ohlc_sanity(df, col_map)

    # Sample rows
    report["head"] = df.head(5).to_dict(orient="records")
    report["tail"] = df.tail(5).to_dict(orient="records")

    return report


def print_human_readable(report: Dict) -> None:
    print("\n=== Data Shape ===")
    print(f"rows: {report.get('shape', [None, None])[0]}, cols: {report.get('shape', [None, None])[1]}")

    print("\n=== Columns & Dtypes ===")
    schema = report.get("schema", {})
    for col, info in schema.items():
        print(f"- {col}: dtype={info.get('dtype')} non_null={info.get('non_null')} nulls={info.get('nulls')}")

    print("\n=== Time Analysis ===")
    print(json.dumps(report.get("time_analysis", {}), indent=2))

    print("\n=== OHLC Sanity ===")
    print(json.dumps(report.get("ohlc_sanity", {}), indent=2))

    print("\n=== Sample Head (5) ===")
    # Limit row width for readability
    head = report.get("head", [])
    if head:
        df_head = pd.DataFrame(head)
        with pd.option_context("display.max_columns", 20, "display.width", 160):
            print(df_head)

    print("\n=== Sample Tail (5) ===")
    tail = report.get("tail", [])
    if tail:
        df_tail = pd.DataFrame(tail)
        with pd.option_context("display.max_columns", 20, "display.width", 160):
            print(df_tail)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect CSV/Excel data columns and intraday minute regularity.")
    parser.add_argument("--file", required=True, help="Path to the data file (.csv/.xlsx/.xlsm/.parquet)")
    parser.add_argument("--sheet", default=None, help="Sheet name (Excel only, optional)")
    parser.add_argument("--sep", default=",", help="CSV separator (default ',')")
    parser.add_argument("--time-col", dest="time_col", default=None, help="Timestamp column name (optional)")
    parser.add_argument("--tz", default="America/New_York", help="Timezone for timestamps (default: America/New_York)")
    parser.add_argument("--out", default=None, help="Optional path to write JSON report")

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Only list sheets for Excel
    if file_path.suffix.lower() in [".xlsx", ".xls", ".xlsm"]:
        sheet_names, _ = read_excel_meta(file_path)
        if sheet_names:
            print("Available sheets:")
            for s in sheet_names:
                print(f"  - {s}")
        else:
            print("No sheet metadata available or failed to read sheets.")

    df = load_data(file_path, args.sheet, args.sep)

    # Detect time column
    time_col = detect_time_column(list(df.columns), args.time_col)

    report = generate_report(df, time_col, args.tz)

    # Print human-readable summary
    print_human_readable(report)

    # Optional JSON output
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report written to: {out_path}")


if __name__ == "__main__":
    main()