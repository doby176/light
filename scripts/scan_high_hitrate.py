#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

TIMESTAMP_CANDIDATES = [
    "timestamp", "time", "datetime", "date", "dt", "Datetime", "Timestamp", "Time"
]
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


def compute_session_vwap(df: pd.DataFrame, close_col: str, vol_col: str) -> pd.Series:
    dollars = df[close_col].astype(float) * df[vol_col].astype(float)
    cum_dollars = dollars.groupby(df["session_date"]).cumsum()
    cum_vol = df[vol_col].groupby(df["session_date"]).cumsum()
    with np.errstate(invalid='ignore', divide='ignore'):
        vwap = cum_dollars / cum_vol.replace(0, np.nan)
    return vwap


def within_time_window(ts: pd.Series, start_hm: str, end_hm: str) -> pd.Series:
    start_h, start_m = map(int, start_hm.split(":"))
    end_h, end_m = map(int, end_hm.split(":"))
    t = ts.dt.time
    return ((t >= pd.Timestamp(hour=start_h, minute=start_m).time()) &
            (t <= pd.Timestamp(hour=end_h, minute=end_m).time()))


def scan_vwap_high_hitrate(df: pd.DataFrame, cols: Dict[str, Optional[str]],
                           z_thresholds: List[float], horizons: List[int], tp_bps_list: List[float],
                           start_hm: str, end_hm: str, cost_bps: float) -> pd.DataFrame:
    time_col, close_col = cols["time"], cols["close"]
    if time_col is None or close_col is None:
        raise ValueError("Missing required columns: time/close")
    if cols["volume"] is None and cols["vwap"] is None:
        raise ValueError("Need volume or vwap column to compute/consume VWAP")

    df = df.copy()
    df["session_date"] = df[time_col].dt.date
    if cols["vwap"] and cols["vwap"] in df.columns:
        df["vwap"] = df[cols["vwap"]].astype(float)
    else:
        vol_col = cols["volume"]
        if vol_col is None:
            raise ValueError("Volume required to compute VWAP")
        df["vwap"] = compute_session_vwap(df, close_col, vol_col)

    df["dev"] = (df[close_col] - df["vwap"]) / df[close_col]

    # Intraday vol for z-scaling (std of 1m returns per day)
    df["ret1m"] = df[close_col].pct_change()
    intraday_std = df.groupby("session_date")["ret1m"].transform(lambda x: x.std(ddof=0))
    with np.errstate(invalid='ignore', divide='ignore'):
        df["z_vwap"] = df["dev"] / intraday_std.replace(0, np.nan)

    # Time window mask
    time_mask = within_time_window(df[time_col], start_hm, end_hm)

    results = []

    for z_thr in z_thresholds:
        long_entries = (df["z_vwap"] <= -z_thr) & time_mask
        short_entries = (df["z_vwap"] >= z_thr) & time_mask

        for H in horizons:
            # Precompute future window stats
            fut_max = df[close_col].shift(-1).rolling(H, min_periods=1).max()
            fut_min = df[close_col].shift(-1).rolling(H, min_periods=1).min()
            fut_close_H = df[close_col].shift(-H)

            for tp_bps in tp_bps_list:
                tp_mult = 1.0 + tp_bps / 1e4
                # Long side
                idx_long = df.index[long_entries]
                if len(idx_long) > 0:
                    entry_px = df.loc[idx_long, close_col]
                    win_reached = fut_max.loc[idx_long] >= entry_px * tp_mult
                    # PnL: wins get TP, losses exit at H; subtract cost
                    ret_long = np.where(win_reached, tp_bps / 1e4, (fut_close_H.loc[idx_long] / entry_px - 1.0)) - (cost_bps / 1e4)
                    wins_long = ret_long > 0
                    n_long = int(len(ret_long))
                    hr_long = float(wins_long.mean()) if n_long else np.nan
                    avg_bps_long = float(np.nanmean(ret_long) * 1e4) if n_long else np.nan
                    results.append({
                        "family": "VWAP_MR", "side": "long", "z_thr": z_thr, "H": H, "tp_bps": tp_bps,
                        "cost_bps": cost_bps, "n_trades": n_long, "hit_rate": hr_long, "avg_bps": avg_bps_long
                    })
                # Short side
                idx_short = df.index[short_entries]
                if len(idx_short) > 0:
                    entry_px = df.loc[idx_short, close_col]
                    win_reached = fut_min.loc[idx_short] <= entry_px / tp_mult
                    ret_short = np.where(win_reached, tp_bps / 1e4, (1.0 - fut_close_H.loc[idx_short] / entry_px)) - (cost_bps / 1e4)
                    wins_short = ret_short > 0
                    n_short = int(len(ret_short))
                    hr_short = float(wins_short.mean()) if n_short else np.nan
                    avg_bps_short = float(np.nanmean(ret_short) * 1e4) if n_short else np.nan
                    results.append({
                        "family": "VWAP_MR", "side": "short", "z_thr": z_thr, "H": H, "tp_bps": tp_bps,
                        "cost_bps": cost_bps, "n_trades": n_short, "hit_rate": hr_short, "avg_bps": avg_bps_short
                    })

    out = pd.DataFrame.from_records(results)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan for high hit-rate intraday setups (VWAP mean reversion with small TP).")
    parser.add_argument("--file", required=True, help="Path to cleaned CSV (RTH)")
    parser.add_argument("--time-col", default=None, help="Timestamp column name (auto-detect if omitted)")
    parser.add_argument("--sep", default=None, help="CSV separator (auto-detect by default)")
    parser.add_argument("--reports", default=None, help="Directory to save results (default: ./reports)")
    parser.add_argument("--cost-bps", type=float, default=1.0, help="Round-trip cost in bps (default 1.0)")
    parser.add_argument("--z-list", default="1.0,1.2,1.5,2.0", help="Comma list of VWAP z thresholds")
    parser.add_argument("--h-list", default="5,10,15,30", help="Comma list of horizons (minutes)")
    parser.add_argument("--tp-bps-list", default="1.0,2.0,3.0,4.0", help="Comma list of take-profit targets in bps")
    parser.add_argument("--start", default="09:40", help="Start time HH:MM (default 09:40)")
    parser.add_argument("--end", default="15:30", help="End time HH:MM (default 15:30)")

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
    if cols["close"] is None:
        print("Could not detect close column", file=sys.stderr)
        sys.exit(1)

    df[cols["time"]] = ensure_datetime(df, cols["time"])  # type: ignore[arg-type]
    df.sort_values(cols["time"], inplace=True)

    reports_dir = Path(args.reports) if args.reports else path.parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    z_list = [float(x) for x in args.z_list.split(",") if x.strip()]
    h_list = [int(x) for x in args.h_list.split(",") if x.strip()]
    tp_bps_list = [float(x) for x in args.tp_bps_list.split(",") if x.strip()]

    results = scan_vwap_high_hitrate(
        df, cols, z_list, h_list, tp_bps_list, args.start, args.end, args.cost_bps
    )

    if results.empty:
        print("No results produced.")
        return

    results["hit_rate_pct"] = results["hit_rate"] * 100.0
    results_sorted = results.sort_values(["hit_rate", "n_trades"], ascending=[False, False])

    out_csv = reports_dir / "high_hitrate_results.csv"
    results_sorted.to_csv(out_csv, index=False)

    # Print top lines and those meeting 70%+ hit rate and reasonable sample size
    meets = results_sorted[(results_sorted["hit_rate_pct"] >= 70.0) & (results_sorted["n_trades"] >= 300)]

    print("Top parameter sets by hit rate:")
    print(results_sorted.head(10).to_string(index=False))

    if not meets.empty:
        print("\nCandidates meeting >=70% hit rate (n>=300):")
        print(meets.head(20).to_string(index=False))
    else:
        print("\nNo parameter sets reached 70% hit rate with the current grid. Consider increasing z threshold, reducing TP bps, shortening horizon, or narrowing time window.")

    print(f"\nFull results saved to: {out_csv}")


if __name__ == "__main__":
    main()