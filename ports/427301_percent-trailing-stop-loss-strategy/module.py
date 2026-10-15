"""SMA 10 / 20 cross with a 10 % trailing stop: the fast SMA crossing above the slow one goes long,
crossing below goes short (each reverses the other side). The source's trailing stop ratchets on
2-hour closes; it is described, not emitted (mark trailing_stop_pending).
Port of FMZ strategy #427301 "Percent Trailing Stop Loss Strategy".

FMZ source id: 427301

Source
    https://www.fmz.com/strategy/427301 (PineScript v4, FMZ last modified 2023-09-19 21:18:39).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 145-182), trail 10 %
    crossover(sma(close, 10), sma(close, 20)) -> entry long; crossunder -> entry short
    long: stop = max(close x 0.90, stop[1]) on each bar close; short: min(close x 1.10, stop[1])

Interpretation choices (Pine rules in SURVEY_README.md; skill 30-strategy-authoring section 7)
    * The trailing level ratchets on the 2-HOUR bar closes and is placed for the next bar. The house
      trail's "close" anchor is the best MINUTE close, so it cannot express a ratchet on 2-hour
      closes exactly (it would trail tighter): rule 2 stays, mark trailing_stop_pending, the trail
      is described in PORT_NOTES.md and quoted in original_sizing.txt, and not emitted.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close entries; the trailing stop is pending (marked).
    2 generic: PASS, MA lengths and a percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trailing stop is quoted in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427301_sma_cross_pct_trail"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 5],
    "slow": [20, 40, 80],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 20, "trail_pct": 10.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, false.copy(), dn, false.copy()


def portfolio_kwargs(**params):
    return {}
