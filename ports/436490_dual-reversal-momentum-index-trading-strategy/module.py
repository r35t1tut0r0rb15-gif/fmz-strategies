"""Stochastic momentum index extremes, 1-hour bars: the signal line of the SMI under -50 on a red candle goes long (closing a short first); over +50 on a green candle goes short; a candle against the position with a large
body (over half the average) closes it.
Port of FMZ strategy #436490 "Dual Reversal Momentum Index Trading Strategy" (Noro's Stochastic Strategy v1.0).

FMZ source id: 436490

Source
    https://www.fmz.com/strategy/436490 (PineScript v2, FMZ last modified 2023-12-25 12:02:57).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 170-225), %K 5, %D 3, limit 50; body filter average / 2
    SMI = avgrel / (avgdiff / 2) 100 (double EMA of the close against the channel midpoint over the double EMA of the range);  SMIsignal = ema(SMI, 3)
    up = SMIsignal < -50 and close < open -> (close short), entry long;  dn = SMIsignal > 50 and close > open -> (close long), entry short;  exit = (long and green or short and red) and body > avg body / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The position-dependent rules use the position at the bar's open. The orders of one bar are filled in
      the script's call order at the next open (close of a short, entry long, close of a long, entry
      short, close_all). The full-equity lot is sizing. REVERSAL INTENDED. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic momentum index and candle colour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital percent and the lot formula stored.
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

NAME = "fmz_436490_noro_stochastic_smi_extremes"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "a": [5, 10],
    "limit": [50, 40],
}
DEFAULT_PARAMS = {"a": 5, "b": 3, "limit": 50}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    a, b = int(p["a"]), int(p["b"])
    ll, hh = lo.rolling(a).min(), h.rolling(a).max()
    diff, rdiff = hh - ll, c - (hh + ll) / 2
    avgrel = rdiff.ewm(span=b, adjust=False).mean().ewm(span=b, adjust=False).mean()
    avgdiff = diff.ewm(span=b, adjust=False).mean().ewm(span=b, adjust=False).mean()
    with np.errstate(invalid="ignore", divide="ignore"):
        smi = (avgrel / (avgdiff / 2) * 100).where(avgdiff != 0, 0.0)
    sig = smi.ewm(span=b, adjust=False).mean()
    body = (c - o).abs()
    abody = body.rolling(10).mean()
    limit = float(p["limit"])
    up = ((sig < -limit) & (c < o)).fillna(False).to_numpy()
    dn = ((sig > limit) & (c > o)).fillna(False).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    big = (body > abody / 2).fillna(False).to_numpy()
    m = len(up)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos = 1
                elif op == "eS" and pos >= 0:
                    pos = -1
                elif op == "XS" and pos < 0:
                    pos = 0
                elif op == "XL" and pos > 0:
                    pos = 0
                elif op == "X" and pos != 0:
                    pos = 0
        held[i] = pos
        ops = []
        if up[i]:
            if pos < 0:
                ops.append("XS")
            ops.append("eL")
        if dn[i]:
            if pos > 0:
                ops.append("XL")
            ops.append("eS")
        if ((pos > 0 and green[i]) or (pos < 0 and red[i])) and big[i]:
            ops.append("X")
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
