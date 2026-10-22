"""Bollinger %B dips, 1-hour bars, long only: %B (20, 2) under 0 goes long, with a 5 % target from the entry (the 100 % stop sits at zero).
Port of FMZ strategy #440695 "基于布林带B指标的长线交易策略Long-Term-Trading-Strategy-Based-on-Bollinger-Bands-B-Indicator" (BB %B Long Strategy).

FMZ source id: 440695

Source
    https://www.fmz.com/strategy/440695 (PineScript v5, FMZ last modified 2024-02-01 11:15:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-169), BB 20 / 2 on close; take profit 5 %, stop loss 100 %; %B level 0; dates 2023-2024 (unused)
    percentB = (close - lower) / (upper - lower);  percentB < 0 -> entry Long and strategy.exit(limit = avg price x 1.05, stop = avg price x (1 - 100 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent only on signal bars: on the first one the position is still flat (average price
      na) and nothing is placed, so in the script the target starts with the next %B < 0 bar of the
      trade (usually the following bar). The port holds tp_stop 0.05 from the fill (stated
      approximation); the 100 % stop is a level at zero and is not needed. The date inputs are unused.
      Pine's stdev is the population deviation. Long only. Stop module: portfolio_kwargs {} (driver D4).
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry (activation approximated).
    2 generic: PASS, Bollinger %B.
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

NAME = "fmz_440695_bb_percent_b_dip_long_target"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.05, 0.02],
    "dev": [2.0, 2.5],
}
DEFAULT_PARAMS = {"tp": 0.05, "dev": 2.0, "length": 20, "level": 0.0}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    up, lo = basis + float(p["dev"]) * sd, basis - float(p["dev"]) * sd
    pb = (c - lo) / (up - lo).where(up > lo)
    sig = (pb < float(p["level"])).to_numpy()
    t_ = float(p["tp"])
    ov, hv = bars_df["open"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and hv[i] >= ov[entry_i] * (1 + t_):
            pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
