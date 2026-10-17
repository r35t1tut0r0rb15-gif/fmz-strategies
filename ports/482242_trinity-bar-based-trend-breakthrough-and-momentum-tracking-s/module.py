"""Two consecutive bars closing in the upper third of their range (the second opening in its lower or upper third) go
long, the lower-third mirror goes short, always in, hourly bars.
Port of FMZ strategy #482242 "三段趋势突破与动量跟踪策略-Trinity-Bar-Based-Trend-Breakthrough-and-Momentum-Tracking-Strategy" (TrinityBar).

FMZ source id: 482242

Source
    https://www.fmz.com/strategy/482242 (PineScript v5, FMZ last modified 2025-02-17 10:53:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 114-187), thirds of each bar's range
    validBuy = previous bar closes in its upper third (any open) and this bar opens in its lower or upper third and
    closes in its upper third -> close short, entry long when not long; validSell mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * A zero-range bar meets both patterns: neither is taken. The closes repeat the reversal (REVERSAL INTENDED);
      always in. Signal module, no stops. FREQ = "1h" from the backtest header. #482428 (L36) is this pattern with a
      previous-bar trailing stop on daily bars.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, thirds of each bar's range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: ND482242 with #482428 (Jaccard 0.770, similar, not a duplicate); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482242_trinity_bar_thirds_always_in"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
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


def simulate(bars_df, **params):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    rng = h - lo
    lt, ut = lo + rng / 3, h - rng / 3
    up_c, dn_c = c >= ut, c <= lt
    o_ends = (o <= lt) | (o >= ut)
    buy = up_c.shift(1, fill_value=False) & o_ends & up_c
    sell = dn_c.shift(1, fill_value=False) & o_ends & dn_c
    long_e = (buy & ~sell).astype(bool)
    short_e = (sell & ~buy).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
