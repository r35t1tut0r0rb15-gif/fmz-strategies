"""Bollinger breakouts with an RSI window, 1-hour bars: the close crossing over the upper band (20, 2 sd) with the RSI 14 between 60 and 70 goes long (closed when the close crosses back
under the basis); the close crossing under the lower band with the RSI between 35 and 40 goes short (closed over the basis).
Port of FMZ strategy #436226 "Bollinger Momentum Breakout Strategy" (Bollinger Band Breakout (BB-Stoxguru)).

FMZ source id: 436226

Source
    https://www.fmz.com/strategy/436226 (PineScript v4, FMZ last modified 2023-12-22 13:09:32).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 129-151), Bollinger 20 / 2 sd; RSI 14 windows 60-70 and 35-40
    entry long: crossover(close, upper) and 60 <= rsi <= 70;  close long: crossunder(close, basis);  entry short: crossunder(close, lower) and 35 <= rsi <= 40;  close short: crossover(close, basis)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four orders of one bar are filled in the script's call order at the next open (entry long, close
      long, entry short, close short). The 2007 start date is the author's backtest window: dropped (an
      order of the form time >= start is always true on the data). REVERSAL INTENDED. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band breakouts with an RSI window.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_436226_bollinger_breakout_rsi_window"
FAMILY = "bollinger_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14}


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
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    r = int(p["rsi_len"])
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    e_l = ((c > upper) & (c.shift(1) <= upper.shift(1)) & (rsi >= 60) & (rsi <= 70)).fillna(False).to_numpy()
    c_l = ((c < basis) & (c.shift(1) >= basis.shift(1))).fillna(False).to_numpy()
    e_s = ((c < lower) & (c.shift(1) >= lower.shift(1)) & (rsi <= 40) & (rsi >= 35)).fillna(False).to_numpy()
    c_s = ((c > basis) & (c.shift(1) <= basis.shift(1))).fillna(False).to_numpy()
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
        pend = (bool(e_l[i]), bool(c_l[i]), bool(e_s[i]), bool(c_s[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
