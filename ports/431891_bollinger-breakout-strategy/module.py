"""Noro's Bollinger fades on ohlc4, 30-minute bars: a close at or under the lower band (20, 2) goes long, at or over the
upper band goes short; a green bar closes a long, a red bar of real body closes a short. Adds are not ported.
Port of FMZ strategy #431891 "Bollinger Breakout Strategy" (Noro's Bollinger Strategy v1.1).

FMZ source id: 431891

Source
    https://www.fmz.com/strategy/431891 (PineScript v2, FMZ last modified 2023-11-13 10:19:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 190-238), BB 20 / 2 of ohlc4, body EMA 30, pyramiding 5
    up = close <= lower -> entry long;  dn = close >= upper -> entry short
    exit = (long and close > open) or (short and close < open) and body > ema(body, 30) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine precedence: "a or b and c" is a or (b and c), so the body filter applies to the short's
      exit only, as written. pyramiding 5: adds are not ported (one net position).
    * A close_all written after an entry acts on the position held at the bar's start and leaves the
      bar flat (C31-C39 convention). The 2018-2100 window is dropped. stdev is the population
      deviation. strategy.entry reverses: REVERSAL INTENDED. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, Bollinger bands and bar colour / body filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and pyramiding 5 stored in original_sizing.txt.
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

NAME = "fmz_431891_noro_bollinger_fade"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    n = int(p["length"])
    basis, sd = src.rolling(n).mean(), src.rolling(n).std(ddof=0)
    up = (c <= basis - p["mult"] * sd).to_numpy()
    dn = (c >= basis + p["mult"] * sd).to_numpy()
    body = (c - o).abs()
    big = (body > body.ewm(span=30, adjust=False).mean() / 2).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up[i]:
            pos = 1
        if dn[i]:
            pos = -1
        if (start == 1 and green[i]) or (start == -1 and red[i] and big[i]):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
