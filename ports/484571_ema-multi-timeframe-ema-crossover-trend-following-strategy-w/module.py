"""EMA 5 crossing both EMA 8 and EMA 13 on one bar, with a percent trailing stop from the best high / low, 1-minute bars:
EMA 5 crossing above EMA 8 and EMA 13 together goes long; crossing below both goes short; each trade trails a stop
10 % (as written) under the highest high since entry (over the lowest low for shorts).
Port of FMZ strategy #484571 "多重时框EMA交叉趋势跟踪策略结合支阻力与智能追踪止损系统-Multi-Timeframe-EMA-Crossover-Trend-Following-Strategy-with-Support-Resistance-and-Smart-Trailing-Stop-System" (EMA Crossover Strategy with S/R and Cross Exits v6).

FMZ source id: 484571

Source
    https://www.fmz.com/strategy/484571 (PineScript v6, FMZ last modified 2025-03-03 09:25:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 186-252), EMA 5 / 8 / 13, trail offset input 0.10
    buy = crossover(ema5, ema8) and crossover(ema5, ema13) -> entry long, close short (sell mirrored)
    long: maxHigh = highest high since the entry bar; longStop = max(longStop, maxHigh x (1 - 0.10)); exit(stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail input is labelled "%" but used as a fraction: x (1 - 0.10) is a 10 % trail, as written (the 0.1 %
      reading is the GRID variant). The level follows the highest high from the fill bar on, ratchets and applies
      from the next bar: the house trail {"type": "percent", "pct": 0.10, "anchor": "high_low"} (best minute high up
      to the previous minute; the same granularity on 1-minute bars). Mark trailing_stop.
    * The hourly S/R values feed plots only. The close after each entry is the reversal itself (REVERSAL INTENDED).
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; trail from the fill (house trail).
    2 generic: PASS, EMAs and a percentage trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the trail ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_484571_ema5_double_cross_pct_trail"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_frac": [0.10, 0.001],
    "slow": [13, 21],
}
DEFAULT_PARAMS = {"fast": 5, "mid": 8, "slow": 13, "trail_frac": 0.10}


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
    e5, e8, e13 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow"))

    def x(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))
    long_e = (x(e5, e8) & x(e5, e13)).astype(bool)
    short_e = (x(e8, e5) & x(e13, e5)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": p["trail_frac"], "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
