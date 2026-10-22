"""KAMA slope filter, 1-hour bars, long only: the KAMA (14, fast 2, slow 20) rising by more than one 14-bar deviation of its own change goes long; falling by more than half a deviation closes (the default
exit; the ATR-trail and PSAR exits are off).
Port of FMZ strategy #440444 "Trend Following Strategy Based on Adaptive Moving Average" (KAMA Strategy - Kaufman's Adaptive Moving Average).

FMZ source id: 440444

Source
    https://www.fmz.com/strategy/440444 (PineScript v4, FMZ last modified 2024-01-30 16:30:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 175-337), KAMA 1: 14 / 2 / 20 (KAMA 2-8 plotted only); entry filter 1, exit filter 0.5; KAMA exit on, ATR trail off, PSAR off
    kama := sc x close + (1 - sc) x nz(kama[1]), sc = (er (2/3 - 2/21) + 2/21)^2, er = |change(close, 14)| / sum(|change(close)|, 14);  delta = kama - kama[1]
    long = delta > 0 and delta > 1 x stdev(delta, 14) -> entry Buy;  longClose = delta < 0 and |delta| > 0.5 x stdev(delta, 14) (with the PSAR / ATR parts off) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The KAMA keeps the script's nz() start, so it grows from 0 after the first 14 bars (a long
      warm-up, as written). With the PSAR and ATR-trail switches off their terms are na and drop out
      of the or. Pine's stdev is the population deviation. Long only. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive average slope against its own deviation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440444_kama_slope_filter_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length1": [14, 30],
    "exit_filter": [0.5, 1.0],
}
DEFAULT_PARAMS = {"length1": 14, "exit_filter": 0.5, "fast1": 2, "slow1": 20, "entry_filter": 1.0}


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


def _kama(c, n, fast, slow):
    mom = (c - c.shift(n)).abs()
    vol = c.diff().abs().rolling(n).sum()
    er = (mom / vol.where(vol != 0)).where(vol != 0, 0.0).where(mom.notna() & vol.notna())
    fa, sa = 2 / (fast + 1), 2 / (slow + 1)
    sc = ((er * (fa - sa)) + sa) ** 2
    sv, cv = sc.to_numpy(dtype=float), c.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    prev = np.nan
    for i in range(len(cv)):
        k = sv[i] * cv[i] + (1 - sv[i]) * (0.0 if np.isnan(prev) else prev)
        out[i] = k
        prev = k
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length1"])
    k = _kama(c, n, int(p["fast1"]), int(p["slow1"]))
    dk = k - k.shift(1)
    sd = dk.rolling(n).std(ddof=0)
    buy = (dk > 0) & (dk > float(p["entry_filter"]) * sd)
    sell = (dk < 0) & (dk.abs() > float(p["exit_filter"]) * sd)
    false = pd.Series(False, index=c.index)
    return buy, sell, false, false.copy()


def portfolio_kwargs(**params):
    return {}
