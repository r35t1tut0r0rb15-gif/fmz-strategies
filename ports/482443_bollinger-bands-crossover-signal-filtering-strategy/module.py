"""The side of the latest Bollinger 55 / 1 band break, 2-hour bars: when the last close above the upper band becomes more recent than the last close below the lower band, go long; the mirror goes short; reversing.
Port of FMZ strategy #482443 "Bollinger Bands Crossover Signal Filtering Strategy" (Bollinger Bands Filter [Strategy]).

FMZ source id: 482443

Source
    https://www.fmz.com/strategy/482443 (PineScript v5, FMZ last modified 2025-02-18 14:47:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-152), BB SMA 55, 1 sd
    L1 = barssince(close > upper);  S1 = barssince(close < lower);  L1 < S1 and not (L1 < S1)[1] -> entry Long;  S1 < L1 and not (S1 < L1)[1] -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * barssince is na before the first break, and a comparison with na is false, so no signal comes
      until both sides have broken once. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger break-side switches.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_482443_bb55_1sd_break_side_switch_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [55, 20],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 55, "mult": 1.0}


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


def _barssince(flag):
    """ta.barssince: bars since flag was last true (na before the first)."""
    f = np.asarray(flag, dtype=bool)
    idx = np.arange(len(f))
    last = np.maximum.accumulate(np.where(f, idx, -1))
    out = (idx - last).astype(float)
    out[last < 0] = np.nan
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    l1 = pd.Series(_barssince((c > basis + dev).to_numpy()), index=c.index)
    s1 = pd.Series(_barssince((c < basis - dev).to_numpy()), index=c.index)
    lw, sw = l1 < s1, s1 < l1
    le = lw & ~lw.shift(1, fill_value=False)
    se = sw & ~sw.shift(1, fill_value=False)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
