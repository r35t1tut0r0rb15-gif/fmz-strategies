""""Thirds" bar sequences, hourly bars: after a bar closing in its upper third, a bar that closes in its upper third from the lower or upper third goes long; the mirror goes short; reversing.
Port of FMZ strategy #482242 "Trinity Bar Based Trend Breakthrough and Momentum Tracking Strategy" (TrinityBar).

FMZ source id: 482242

Source
    https://www.fmz.com/strategy/482242 (PineScript v5, FMZ last modified 2025-02-17 10:53:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-189), bar thirds (current and previous bar); 200 % of equity, capital 100000
    validBuy = prev bar 1-3 / 2-3 / 3-3 and current bar 1-3 or 3-3 -> close Short, entry Long if not long;  validSell = prev 2-1 / 1-1 / 3-1 and current 1-1 or 3-1 -> close Long, entry Short if not short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each signal closes the other side and enters, which is a reversal; on a zero-range bar both types
      hold and the later short call wins (#437773). REVERSAL INTENDED. The 200 % of equity size and
      capital are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bar-thirds continuation sequences.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: ND482242 (2 members, best partner #482428, Jaccard 0.770); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482242_trinity_bar_thirds_sequence_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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


def _types(o, h, lo, c):
    rng = h - lo
    lt, ut = lo + rng / 3, h - rng / 3
    up_close, dn_close = c >= ut, c <= lt
    open_lo, open_hi = o <= lt, o >= ut
    open_mid = (o > lt) & (o < ut)
    bull_any = up_close & (open_lo | open_hi | open_mid)
    bear_any = dn_close & (open_lo | open_hi | open_mid)
    bull_13_33 = up_close & (open_lo | open_hi)
    bear_11_31 = dn_close & (open_lo | open_hi)
    return bull_any, bear_any, bull_13_33, bear_11_31


def simulate(bars_df, **params):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    bull_any, bear_any, bull_now, bear_now = _types(o, h, lo, c)
    le = bull_any.shift(1, fill_value=False) & bull_now
    se = bear_any.shift(1, fill_value=False) & bear_now
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
