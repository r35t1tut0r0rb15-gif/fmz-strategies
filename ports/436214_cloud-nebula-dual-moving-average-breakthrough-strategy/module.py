"""Two EMA clouds of highs and lows, 1-minute bars: with the fast cloud (60) entirely under the slow one (240) a close crossing over the slow cloud's top goes long (exits: a close under
the lowest close of the last 240 bars as stored at the entry, or the fast cloud above the slow one with a close under its floor); the mirror goes short.
Port of FMZ strategy #436214 "Cloud Nebula Dual Moving Average Breakthrough Strategy" (High Low Cloud Strategy Backtesting).

FMZ source id: 436214

Source
    https://www.fmz.com/strategy/436214 (PineScript v4, FMZ last modified 2023-12-22 11:48:28).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 128-171), clouds EMA 60 / 240 of high and low
    ycloud_entry = c1_high < c2_low and crossover(close, c2_high) -> entry long;  stoploss = crossunder(close, valuewhen(ycloud_entry, lowest(close[1], 240), 0));  takeprofit = c1_low > c2_high and crossunder(close, c1_low) -> close long
    xcloud_entry = c1_low > c2_high and crossunder(close, c2_low) -> entry short;  stoploss = crossover(close, valuewhen(xcloud_entry, highest(close[1], 240), 0));  takeprofit = c1_high < c2_low and crossover(close, c1_high) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stored stop level is the lowest (highest) close of the 240 bars before the latest entry
      SIGNAL (kept until the next one, even when that entry added nothing). The exits are rules on bar closes
      filled at the next open: close-based exit signals. The orders of one bar are filled in the script's call
      order at the next open (entry long, close long, entry short, close short). REVERSAL INTENDED. FREQ
      = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, cloud crossings.
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

NAME = "fmz_436214_high_low_cloud_cross"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "c1": [60, 30],
    "c2": [240, 120],
}
DEFAULT_PARAMS = {"c1": 60, "c2": 240}


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


def _xo(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False).to_numpy()


def _xu(a, b):
    return ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False).to_numpy()


def _stored(cond, src):
    """Pine valuewhen(cond, src, 0): the value of src at the latest bar where cond was true (NaN before)."""
    out = np.full(len(src), np.nan)
    last = np.nan
    for i in range(len(src)):
        if cond[i]:
            last = src[i]
        out[i] = last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n1, n2 = int(p["c1"]), int(p["c2"])
    c1_high, c1_low = h.ewm(span=n1, adjust=False).mean(), lo.ewm(span=n1, adjust=False).mean()
    c2_high, c2_low = h.ewm(span=n2, adjust=False).mean(), lo.ewm(span=n2, adjust=False).mean()
    y_entry = ((c1_high < c2_low).to_numpy() & _xo(c, c2_high))
    x_entry = ((c1_low > c2_high).to_numpy() & _xu(c, c2_low))
    low_prior = c.shift(1).rolling(n2).min().to_numpy()
    high_prior = c.shift(1).rolling(n2).max().to_numpy()
    y_level = pd.Series(_stored(y_entry, low_prior), index=c.index)
    x_level = pd.Series(_stored(x_entry, high_prior), index=c.index)
    y_stop = _xu(c, y_level)
    y_tp = ((c1_low > c2_high).to_numpy() & _xu(c, c1_low))
    x_stop = _xo(c, x_level)
    x_tp = ((c1_high < c2_low).to_numpy() & _xo(c, c1_high))
    m = len(y_entry)
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
        pend = (bool(y_entry[i]), bool(y_tp[i] or y_stop[i]), bool(x_entry[i]), bool(x_tp[i] or x_stop[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
