"""Donchian breakouts with a midline exit, 1-hour bars: a close over the previous 10-bar high goes long (closed when the close falls under the channel
midline); a close under the previous 10-bar low goes short (closed over the midline). The optional stop is off.
Port of FMZ strategy #435981 "Momentum Capture Channel Strategy" (Donchian Channel Strategy Idea).

FMZ source id: 435981

Source
    https://www.fmz.com/strategy/435981 (PineScript v4, FMZ last modified 2023-12-20 15:46:40).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 171-200), high period 10, low period 10; long only off; stop loss off (5 %)
    enter_long = close > highest(high, 10)[1];  exit_long = close < (highest(high, 10) + lowest(low, 10)) / 2;  enter_short = close < lowest(low, 10)[1];  exit_short = close > midline
    entry long, close long, entry short, close short (shorts when long_only is false);  exit(stop = avg (1 -+ 5 %)) only when use_sl

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel for the entry is the previous bar's; the midline includes the current bar, as
      written. The four orders of one bar are filled in the script's call order at the next open (entry
      long, close long, entry short, close short); a bar that enters and meets its own exit ends
      flat. The stop is off by default and not ported. REVERSAL INTENDED. The full-equity size is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, stop switch off by default: not ported.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and commission stored.
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

NAME = "fmz_435981_donchian_midline_exit"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "high_period": [10, 20],
    "low_period": [10, 20],
}
DEFAULT_PARAMS = {"high_period": 10, "low_period": 10}


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
    hh = h.rolling(int(p["high_period"])).max()
    ll = lo.rolling(int(p["low_period"])).min()
    base = (hh + ll) / 2
    e_l = (c > hh.shift(1)).fillna(False).to_numpy()
    x_l = (c < base).fillna(False).to_numpy()
    e_s = (c < ll.shift(1)).fillna(False).to_numpy()
    x_s = (c > base).fillna(False).to_numpy()
    m = len(e_l)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            a, b, cc, d = pend
            if a and pos <= 0:
                pos = 1
            if b and pos == 1:
                pos = 0
            if cc and pos >= 0:
                pos = -1
            if d and pos == -1:
                pos = 0
        held[i] = pos
        pend = (bool(e_l[i]), bool(x_l[i]), bool(e_s[i]), bool(x_s[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
