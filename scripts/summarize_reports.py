#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def minute_to_clock(minute_of_day: int) -> str:
    hour = minute_of_day // 60
    minute = minute_of_day % 60
    return f"{hour:02d}:{minute:02d}"


def summarize_minute_of_day(reports_dir: Path) -> str:
    path = reports_dir / "minute_of_day_seasonality.csv"
    if not path.exists():
        return "- Minute-of-day: report not found."
    df = pd.read_csv(path)
    df["ret_mean_bps"] = df.get("ret_mean_bps", df.get("ret_mean", 0) * 1e4)

    top = df.sort_values("ret_mean_bps", ascending=False).head(10).copy()
    bot = df.sort_values("ret_mean_bps", ascending=True).head(10).copy()

    top_list = ", ".join([f"{minute_to_clock(int(r.minute_of_day))} ({r.ret_mean_bps:.1f} bps)" for r in top.itertuples()])
    bot_list = ", ".join([f"{minute_to_clock(int(r.minute_of_day))} ({r.ret_mean_bps:.1f} bps)" for r in bot.itertuples()])

    overall_mean = df["ret_mean_bps"].mean()

    lines = [
        "- Minute-of-day seasonality:",
        f"  - Best 10 minutes: {top_list}",
        f"  - Worst 10 minutes: {bot_list}",
        f"  - Overall average 1-min return: {overall_mean:.2f} bps",
    ]
    return "\n".join(lines)


def summarize_vwap(reports_dir: Path) -> str:
    path = reports_dir / "vwap_reversion_fwd15m.csv"
    if not path.exists():
        return "- VWAP reversion: report not found."
    df = pd.read_csv(path)
    if df.empty:
        return "- VWAP reversion: no data."

    # Compute a coarse mean-reversion score: correlation between bin center and mean_bps (negative implies reversion)
    bin_map = {
        "<-2": -2.25, "-2..-1.5": -1.75, "-1.5..-1": -1.25, "-1..-0.5": -0.75,
        "-0.5..0": -0.25, "0..0.5": 0.25, "0.5..1": 0.75, "1..1.5": 1.25, "1.5..2": 1.75, ">2": 2.25,
    }
    df["bin_center"] = df["z_bin"].map(bin_map)
    df = df.dropna(subset=["bin_center", "mean_bps"]) if "mean_bps" in df.columns else df.dropna(subset=["bin_center", "mean"])  # type: ignore
    if "mean_bps" not in df.columns:
        df["mean_bps"] = df["mean"] * 1e4

    # Weighted correlation by count
    x = df["bin_center"].to_numpy()
    y = df["mean_bps"].to_numpy()
    w = df["count"].to_numpy() if "count" in df.columns else np.ones_like(x)
    # Weighted correlation
    x_mean = np.average(x, weights=w)
    y_mean = np.average(y, weights=w)
    num = np.average((x - x_mean) * (y - y_mean), weights=w)
    den = np.sqrt(np.average((x - x_mean) ** 2, weights=w) * np.average((y - y_mean) ** 2, weights=w))
    corr = float(num / den) if den > 0 else 0.0

    direction = "mean-reverting" if corr < 0 else "trend-following"

    # Key bins to show
    key_bins = ["<-2", "-1..-0.5", "-0.5..0", "0..0.5", "0.5..1", ">2"]
    shown = df.set_index("z_bin").reindex(key_bins).dropna(subset=["mean_bps"], how="all")
    sample = ", ".join([f"{k}: {v:.1f} bps" for k, v in shown["mean_bps"].to_dict().items()])

    lines = [
        "- VWAP deviation reversion (15m forward):",
        f"  - Behavior: {direction} (weighted corr between z and fwd return = {corr:.2f})",
        f"  - Sample by z-bins (mean fwd 15m bps): {sample}",
    ]
    return "\n".join(lines)


def summarize_orb(reports_dir: Path) -> str:
    # ORB file name is dynamic; default created by our script
    candidates = list(reports_dir.glob("orb_*m_fwd*m.csv"))
    if not candidates:
        return "- Opening Range Breakout: report not found."
    path = candidates[0]
    df = pd.read_csv(path)
    if df.empty:
        return "- Opening Range Breakout: no trades found."

    df["ret_bps"] = df.get("ret_bps", df["ret"] * 1e4)
    mean_bps = float(df["ret_bps"].mean())
    median_bps = float(df["ret_bps"].median())
    hit_rate = float((df["ret_bps"] > 0).mean())
    n = int(len(df))

    by_side = df.groupby("side")["ret_bps"].agg(["mean", "median", "count"]).rename(columns={"mean": "mean_bps", "median": "median_bps", "count": "n"})
    side_parts = []
    for side, row in by_side.iterrows():
        side_parts.append(f"{side}: mean {row.mean_bps:.1f} bps, median {row.median_bps:.1f} bps, n={int(row.n)}")

    lines = [
        "- Opening Range Breakout (15m -> 30m):",
        f"  - Overall: mean {mean_bps:.1f} bps, median {median_bps:.1f} bps, hit-rate {hit_rate*100:.1f}%, n={n}",
        f"  - By side: {"; ".join(side_parts)}",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize intraday edge reports into readable insights.")
    parser.add_argument("--reports", required=True, help="Path to reports directory")
    parser.add_argument("--out-md", default=None, help="Optional path to write a Markdown summary")

    args = parser.parse_args()
    reports_dir = Path(args.reports)
    if not reports_dir.exists():
        print(f"Reports dir not found: {reports_dir}")
        return

    sections = [
        summarize_minute_of_day(reports_dir),
        summarize_vwap(reports_dir),
        summarize_orb(reports_dir),
    ]
    summary_text = "\n".join(sections)

    print("\n=== Insights Summary ===\n")
    print(summary_text)

    if args.out_md:
        out_path = Path(args.out_md)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("# Intraday Edge Insights\n\n")
            f.write(summary_text.replace("\n- ", "\n- "))
            f.write("\n")
        print(f"\nMarkdown summary written to: {out_path}")


if __name__ == "__main__":
    main()