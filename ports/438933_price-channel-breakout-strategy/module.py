"""Noro's price channel pullbacks, 1-hour bars: two red bars with a large body above the 30-bar close channel centre go long, two green bars under it go short; a signal against an open position only
flattens it; a large-bodied bar in the trade's favour closes it.
Port of FMZ strategy #438933 "Price Channel Breakout Strategy" (Price Channel str 1.0).

FMZ source id: 438933

Source
    https://www.fmz.com/strategy/438933 (PineScript v2, FMZ last modified 2024-01-16 14:22:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 184-229), channel 30 on closes; long and short on; date window 1900-2100
    up = sma(bar, 2) == -1 and close > center and body > sma(body, 10) / 2;  dn = sma(bar, 2) == 1 and close < center and body > it
    up: short -> close_all, entry Long;  dn: long -> close_all, entry Short;  exit = (long and close > open or short and close < open) and body > sma(body, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The final close_all is written after the entries; it acts on the position held at the bar close
      and the bar ends flat (as #430380). A signal against a position also meets the exit test on the
      same bar (its bar colour is the exit colour), so it flattens the position; from flat the signal
      opens. Same-side signals while in a position are ignored (pyramiding 0). REVERSAL INTENDED (by the
      entry order; in effect positions end flat first). The 100 % of equity size is sizing. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel centre, bar colours and body size.
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

NAME = "fmz_438933_noro_price_channel_pullback"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pch": [30, 60],
    "body_ratio": [0.5, 1.0],
}
DEFAULT_PARAMS = {"pch": 30, "body_ratio": 0.5}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["pch"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    bar = np.sign(c - o)
    sb = bar.rolling(2).mean()
    body = (c - o).abs()
    big = (body > body.rolling(10).mean() * float(p["body_ratio"])).to_numpy()
    up = ((sb == -1) & (c > center)).to_numpy() & big
    dn = ((sb == 1) & (c < center)).to_numpy() & big
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        ex = ((pos == 1 and green[i]) or (pos == -1 and red[i])) and big[i]
        if up[i]:
            new = 0 if pos == -1 else (1 if pos == 0 else pos)
        elif dn[i]:
            new = 0 if pos == 1 else (-1 if pos == 0 else pos)
        else:
            new = pos
        if ex:
            new = 0
        if i + 1 >= m and pos == 0:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
