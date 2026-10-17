"""RSI 2 pullbacks in the EMA 50 / 200 trend with a trailing stop, 1-hour bars: with the EMA 50 above the EMA 200 and the
close above the EMA 200, RSI 2 under 10 goes long; the down-trend mirror with RSI 2 over 90 goes short (reversing). Each
trade trails a stop from its best high / low.
Port of FMZ strategy #435132 "基于RSI指标的趋势跟踪止损策略Scalping-Strategy-based-on-RSI-Indicator-with-Trailing-Stop-Loss" (Scalping using RSI 2 indicator).

FMZ source id: 435132

Source
    https://www.fmz.com/strategy/435132 (PineScript v4, FMZ last modified 2023-12-12 15:46:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 156-246), RSI 2, 10 / 90; EMA 50 / 200; trend filter on; "ticker size" input 0.5; trailing stop 1 %
    long = ema50 > ema200 and close > ema200 and rsi2 < 10 -> entry long;  short mirror with rsi2 > 90
    exit(trail_points = 0, trail_offset = close x (1 / 0.5) x 1 % ticks) for each side   (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is active from the entry (trail_points 0) with an offset of close x 2 % ticks: with
      BTC's 0.1 tick that is 0.2 % of the price (the author's 1 % assumed a tick of 0.5). It is ported
      natively (mark trailing_stop): {"type": "percent", "pct": 0.002, "anchor": "high_low"}; the
      script re-sizes the offset from each bar's close (approximation stated; the intended 1 % is in
      the grid).
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The
      date window (2021 to 2024) is the author's: dropped. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, the tick-sized offset -> a percent of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the trail inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435132_rsi2_trend_pullback_trail"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.002, 0.01],
    "os": [10, 20],
}
DEFAULT_PARAMS = {"rsi_len": 2, "os": 10, "slow": 200, "fast": 50, "trail_pct": 0.002}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    os_ = float(p["os"])
    le = ((fast > slow) & (c > slow) & (rsi < os_)).astype(bool)
    se = ((fast < slow) & (c < slow) & (rsi > 100 - os_)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
