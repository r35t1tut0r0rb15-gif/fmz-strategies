"""Stochastic (15, 4, 5) crossing up below 15 on a higher low goes long, crossing down above 85 on a lower high goes
short, with a 3.7 % stop and a 1.8 % target from the signal close, hourly bars.
Port of FMZ strategy #482590 "多时框随机震荡指标策略与趋势确认交易系统-Multi-Timeframe-Stochastic-Oscillator-Strategy-with-Trend-Confirmation-Trading-System" (Swing Fairas Oil).

FMZ source id: 482590

Source
    https://www.fmz.com/strategy/482590 (PineScript v5, FMZ last modified 2025-02-19 10:53:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-158), stochastic 15 / 4 / 5 (85 / 15), SL 3.7 %, TP 1.8 %
    crossover(k, d) and k < 15 and low > lowest(low[1], 5) -> entry long with exit(stop = close x 0.963,
    limit = close x 1.018); crossunder(k, d) and k > 85 and high < highest(high[1], 5) -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 30- and 60-minute stochastics are requested but feed no order (the 30-minute one would be a lower
      timeframe on the hourly chart).
    * The bracket is placed with the entry: 3.7 % / 1.8 % of the signal close, re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, a stochastic, prior extremes and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482590_stoch_extreme_cross_swing_filter_pct_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [3.7, 2.0],
    "tp_pct": [1.8, 3.6],
}
DEFAULT_PARAMS = {"length": 15, "k_smooth": 4, "d_smooth": 5, "ob": 85.0, "os": 15.0, "sl_pct": 3.7, "tp_pct": 1.8}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    up = (k > d) & (k.shift(1) <= d.shift(1))
    dn = (k < d) & (k.shift(1) >= d.shift(1))
    higher_low = lo > lo.shift(1).rolling(5).min()
    lower_high = h < h.shift(1).rolling(5).max()
    long_e = (up & (k < p["os"]) & higher_low).astype(bool)
    short_e = (dn & (k > p["ob"]) & lower_high).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
