#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Optional plotting (handled gracefully if not installed)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except Exception:
    PLOTTING_AVAILABLE = False


TIMESTAMP_CANDIDATES = [
    "timestamp", "time", "datetime", "date", "dt", "Datetime", "Timestamp", "Time"
]
OPEN_CANDIDATES = ["open", "Open", "OPEN"]
HIGH_CANDIDATES = ["high", "High", "HIGH"]
LOW_CANDIDATES = ["low", "Low", "LOW"]
CLOSE_CANDIDATES = ["close", "Close", "CLOSE", "Adj Close", "Adj_Close", "adj_close"]
VOLUME_CANDIDATES = ["volume", "Volume", "VOL", "Vol"]
VWAP_CANDIDATES = ["vw", "vwap", "VWAP", "VW"]


def find_first_present(columns: List[str], candidates: List[str]) -> Optional[str]:
    for cand in candidates:
        if cand in columns:
            return cand
    lower_map = {c.lower(): c for c in columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    return None


def detect_columns(columns: List[str], time_col_user: Optional[str]) -> Dict[str, Optional[str]]:
    time_col = time_col_user if (time_col_user and time_col_user in columns) else find_first_present(columns, TIMESTAMP_CANDIDATES)
    return {
        "time": time_col,
        "open": find_first_present(columns, OPEN_CANDIDATES),
        "high": find_first_present(columns, HIGH_CANDIDATES),
        "low": find_first_present(columns, LOW_CANDIDATES),
        "close": find_first_present(columns, CLOSE_CANDIDATES),
        "volume": find_first_present(columns, VOLUME_CANDIDATES),
        "vwap": find_first_present(columns, VWAP_CANDIDATES),
    }


def load_csv(path: Path, sep: Optional[str]) -> pd.DataFrame:
    if sep is None:
        return pd.read_csv(path, sep=None, engine="python")
    return pd.read_csv(path, sep=sep)


def ensure_datetime(df: pd.DataFrame, time_col: str) -> pd.Series:
    dt = pd.to_datetime(df[time_col], errors="coerce", utc=False)
    if dt.isna().all():
        raise ValueError("Failed to parse timestamps; please check --time-col and data format.")
    return dt


def minute_of_day_index(ts: pd.Series) -> pd.Series:
    return ts.dt.hour * 60 + ts.dt.minute


def compute_vwap_series(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> pd.Series:
    # Prefer provided vwap if present
    if cols["vwap"] and cols["vwap"] in df.columns:
        return df[cols["vwap"]].astype(float)
    # Else compute session VWAP cumulatively per day using close*volume
    close_col, vol_col = cols["close"], cols["volume"]
    if close_col is None or vol_col is None:
        raise ValueError("Need close and volume to compute VWAP if no vw/vwap column present")
    # Group by session day (date part)
    dollars = df[close_col].astype(float) * df[vol_col].astype(float)
    cum_dollars = dollars.groupby(df["session_date"]).cumsum()
    cum_vol = df[vol_col].groupby(df["session_date"]).cumsum()
    with np.errstate(invalid='ignore', divide='ignore'):
        vwap = cum_dollars / cum_vol.replace(0, np.nan)
    return vwap


def minute_of_day_seasonality(df: pd.DataFrame, cols: Dict[str, Optional[str]], reports_dir: Path) -> pd.DataFrame:
    close = cols["close"]
    time_col = cols["time"]
    if close is None or time_col is None:
        raise ValueError("Missing time/close columns for seasonality analysis")

    df_sorted = df.sort_values(time_col).copy()
    df_sorted["ret1m"] = df_sorted[close].pct_change()
    df_sorted["minute_of_day"] = minute_of_day_index(df_sorted[time_col])
    df_sorted["year"] = df_sorted[time_col].dt.year

    season = df_sorted.groupby("minute_of_day")["ret1m"].agg(["mean", "std", "count"]).reset_index()
    season.rename(columns={"mean": "ret_mean", "std": "ret_std", "count": "count"}, inplace=True)
    season["ret_mean_bps"] = season["ret_mean"].fillna(0) * 1e4

    # Save CSV summary
    season_csv = reports_dir / "minute_of_day_seasonality.csv"
    season.to_csv(season_csv, index=False)

    if PLOTTING_AVAILABLE:
        reports_dir.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(12, 4))
        plt.plot(season["minute_of_day"], season["ret_mean_bps"])
        plt.axhline(0, color='k', linewidth=0.8)
        plt.title("Minute-of-day average 1m return (bps)")
        plt.xlabel("Minute of day (0=00:00)")
        plt.ylabel("Avg return (bps)")
        plt.tight_layout()
        plt.savefig(reports_dir / "minute_of_day_avg_return_bps.png", dpi=150)
        plt.close()

        # Yearly heatmap
        pivot = df_sorted.pivot_table(index="year", columns="minute_of_day", values="ret1m", aggfunc="mean") * 1e4
        plt.figure(figsize=(14, 4))
        sns.heatmap(pivot.fillna(0), cmap="coolwarm", center=0)
        plt.title("Minute-of-day avg 1m return (bps) by year")
        plt.xlabel("Minute of day")
        plt.ylabel("Year")
        plt.tight_layout()
        plt.savefig(reports_dir / "minute_of_day_year_heatmap_bps.png", dpi=150)
        plt.close()

    return season


def vwap_reversion(df: pd.DataFrame, cols: Dict[str, Optional[str]], reports_dir: Path, forward_h: int = 15) -> pd.DataFrame:
    close = cols["close"]
    time_col = cols["time"]
    if close is None or time_col is None:
        raise ValueError("Missing time/close columns for VWAP reversion")

    df_sorted = df.sort_values(time_col).copy()
    df_sorted["session_date"] = df_sorted[time_col].dt.date

    vwap = None
    try:
        vwap = compute_vwap_series(df_sorted, cols)
    except Exception as e:
        print(f"Could not compute VWAP from data: {e}", file=sys.stderr)
        return pd.DataFrame()

    df_sorted["vwap"] = vwap
    df_sorted["dev"] = df_sorted[close] - df_sorted["vwap"]

    # Intraday standardization: use per-day std of 1m returns
    df_sorted["ret1m"] = df_sorted[close].pct_change()
    intraday_std = df_sorted.groupby("session_date")["ret1m"].transform(lambda x: x.std(ddof=0))
    # Convert price deviation to z in return terms approximated by dev/price / intraday_std
    with np.errstate(invalid='ignore', divide='ignore'):
        z = (df_sorted["dev"] / df_sorted[close]).replace([np.inf, -np.inf], np.nan) / intraday_std.replace(0, np.nan)
    df_sorted["z_vwap"] = z

    # Forward h-minute return
    df_sorted["fwd_ret"] = df_sorted[close].pct_change(periods=forward_h).shift(-forward_h)

    # Bin by z
    bins = [-np.inf, -2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0, np.inf]
    labels = ["<-2", "-2..-1.5", "-1.5..-1", "-1..-0.5", "-0.5..0", "0..0.5", "0.5..1", "1..1.5", "1.5..2", ">2"]
    df_sorted["z_bin"] = pd.cut(df_sorted["z_vwap"], bins=bins, labels=labels, include_lowest=True)
    cond = df_sorted["z_bin"].notna() & df_sorted["fwd_ret"].notna()
    grouped = df_sorted.loc[cond].groupby("z_bin")["fwd_ret"].agg(["mean", "count"]).reset_index()
    grouped["mean_bps"] = grouped["mean"] * 1e4

    grouped_csv = reports_dir / f"vwap_reversion_fwd{forward_h}m.csv"
    grouped.to_csv(grouped_csv, index=False)

    if PLOTTING_AVAILABLE:
        plt.figure(figsize=(8, 4))
        plt.bar(grouped["z_bin"].astype(str), grouped["mean_bps"])
        plt.axhline(0, color='k', linewidth=0.8)
        plt.title(f"VWAP deviation z vs mean forward {forward_h}m return (bps)")
        plt.ylabel("Mean fwd return (bps)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(reports_dir / f"vwap_reversion_fwd{forward_h}m_bars.png", dpi=150)
        plt.close()

    return grouped


def opening_range_breakout(df: pd.DataFrame, cols: Dict[str, Optional[str]], reports_dir: Path,
                            orb_minutes: int = 15, entry_window_end: str = "12:00", fwd_h: int = 30) -> pd.DataFrame:
    time_col, high_col, low_col, close_col = cols["time"], cols["high"], cols["low"], cols["close"]
    if not all([time_col, high_col, low_col, close_col]):
        raise ValueError("Missing required OHLC/time columns for ORB")

    df_sorted = df.sort_values(time_col).copy()
    df_sorted["session_date"] = df_sorted[time_col].dt.date

    # Define opening range per day: first orb_minutes from 09:30
    df_sorted["time_str"] = df_sorted[time_col].dt.strftime("%H:%M")

    def compute_or(row_group: pd.DataFrame) -> Tuple[float, float, pd.Timestamp]:
        or_start = row_group.iloc[0][time_col].replace(hour=9, minute=30)
        or_end = or_start + pd.Timedelta(minutes=orb_minutes)
        mask_or = (row_group[time_col] >= or_start) & (row_group[time_col] < or_end)
        if not mask_or.any():
            return np.nan, np.nan, pd.NaT
        or_high = row_group.loc[mask_or, high_col].max()
        or_low = row_group.loc[mask_or, low_col].min()
        return or_high, or_low, or_end

    # Compute per-day OR levels
    records = []
    for day, day_df in df_sorted.groupby("session_date"):
        or_high, or_low, or_end = compute_or(day_df)
        if pd.isna(or_high) or pd.isna(or_low) or pd.isna(or_end):
            continue
        # Find first breakout up or down between or_end and entry_window_end
        end_time = pd.Timestamp(str(day)) + pd.Timedelta(hours=int(entry_window_end.split(":")[0]), minutes=int(entry_window_end.split(":")[1]))
        mask_window = (day_df[time_col] >= or_end) & (day_df[time_col] <= end_time)
        window_df = day_df.loc[mask_window]
        long_trigger_idx = window_df.index[window_df[close_col] > or_high].min() if not window_df.empty else None
        short_trigger_idx = window_df.index[window_df[close_col] < or_low].min() if not window_df.empty else None

        trigger_side = None
        trigger_time = None
        if long_trigger_idx is not None and (short_trigger_idx is None or long_trigger_idx < short_trigger_idx):
            trigger_side = "long"
            trigger_time = window_df.loc[long_trigger_idx, time_col]
            entry_price = window_df.loc[long_trigger_idx, close_col]
        elif short_trigger_idx is not None:
            trigger_side = "short"
            trigger_time = window_df.loc[short_trigger_idx, time_col]
            entry_price = window_df.loc[short_trigger_idx, close_col]
        else:
            continue

        exit_time = trigger_time + pd.Timedelta(minutes=fwd_h)
        exit_row = day_df[day_df[time_col] >= exit_time].head(1)
        if exit_row.empty:
            # exit at last close of the day
            exit_price = day_df.iloc[-1][close_col]
        else:
            exit_price = exit_row.iloc[0][close_col]

        ret = (exit_price / entry_price - 1.0) * (1 if trigger_side == "long" else -1)
        records.append({
            "session_date": day,
            "side": trigger_side,
            "trigger_time": trigger_time,
            "entry_price": float(entry_price),
            "exit_price": float(exit_price),
            "fwd_minutes": fwd_h,
            "ret": ret,
        })

    out = pd.DataFrame.from_records(records)
    if out.empty:
        return out

    out["ret_bps"] = out["ret"] * 1e4
    out_csv = reports_dir / f"orb_{orb_minutes}m_fwd{fwd_h}m.csv"
    out.to_csv(out_csv, index=False)

    if PLOTTING_AVAILABLE:
        # Distribution by side
        ax = out.boxplot(column="ret_bps", by="side", grid=False)
        plt.title(f"ORB {orb_minutes}m -> {fwd_h}m fwd returns (bps) by side")
        plt.suptitle("")
        plt.xlabel("Side")
        plt.ylabel("Fwd return (bps)")
        plt.tight_layout()
        plt.savefig(reports_dir / f"orb_{orb_minutes}m_fwd{fwd_h}m_box.png", dpi=150)
        plt.close()

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Run intraday edge scans on cleaned 1-min data (RTH).")
    parser.add_argument("--file", required=True, help="Path to cleaned CSV (RTH only)")
    parser.add_argument("--time-col", dest="time_col", default=None, help="Timestamp column (auto-detect if omitted)")
    parser.add_argument("--sep", default=None, help="CSV separator (auto-detect by default)")
    parser.add_argument("--reports", default=None, help="Directory to save reports (default: ./reports)")

    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    df = load_csv(path, args.sep)
    cols = detect_columns(list(df.columns), args.time_col)
    if cols["time"] is None:
        print("Could not detect timestamp column; pass --time-col", file=sys.stderr)
        sys.exit(1)
    # Parse time, sort
    df[cols["time"]] = ensure_datetime(df, cols["time"])  # type: ignore[arg-type]
    df.sort_values(cols["time"], inplace=True)

    # Reports dir
    reports_dir = Path(args.reports) if args.reports else path.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Add helper columns used by some scans
    df["session_date"] = df[cols["time"]].dt.date

    print("Running minute-of-day seasonality...")
    try:
        season = minute_of_day_seasonality(df, cols, reports_dir)
        top = season.sort_values("ret_mean", ascending=False).head(10)
        bottom = season.sort_values("ret_mean", ascending=True).head(10)
        top.to_csv(reports_dir / "minute_of_day_top10.csv", index=False)
        bottom.to_csv(reports_dir / "minute_of_day_bottom10.csv", index=False)
        print("- Saved: minute_of_day_seasonality.csv, minute_of_day_avg_return_bps.png, minute_of_day_year_heatmap_bps.png, top/bottom CSVs")
    except Exception as e:
        print(f"Seasonality failed: {e}", file=sys.stderr)

    print("Running VWAP reversion (15m forward)...")
    try:
        vwap_res = vwap_reversion(df, cols, reports_dir, forward_h=15)
        if not vwap_res.empty:
            print("- Saved: vwap_reversion_fwd15m.csv and plot")
    except Exception as e:
        print(f"VWAP reversion failed: {e}", file=sys.stderr)

    print("Running Opening Range Breakout (15m -> 30m fwd)...")
    try:
        orb = opening_range_breakout(df, cols, reports_dir, orb_minutes=15, entry_window_end="12:00", fwd_h=30)
        if not orb.empty:
            print("- Saved: ORB CSV and boxplot")
    except Exception as e:
        print(f"ORB failed: {e}", file=sys.stderr)

    print(f"Done. Reports in: {reports_dir}")


if __name__ == "__main__":
    main()