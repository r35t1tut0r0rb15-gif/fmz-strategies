"""Smoothed open channel cross: H = EMA 60 of the 60-bar highest open, L = EMA 60 of the 60-bar
lowest open; SMA 30 of H crossing under SMA 60 of H goes long, SMA 30 of L crossing over SMA 60 of
L goes short (always in the market after the first signal).
Port of FMZ strategy #427071 "Multi-Timeframe Price Channel Strategy".

FMZ source id: 427071

Source
    https://www.fmz.com/strategy/427071 (PineScript v4, FMZ last modified 2023-09-17 18:39:41).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 135-153)
    Sig = security(syminfo.tickerid, '15', open)
    H = ema(highest(Sig, 60), 60); L = ema(lowest(Sig, 60), 60)
    crossunder(sma(H, 30), sma(H, 60)) -> entry long
    crossover(sma(L, 30), sma(L, 60))  -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The chart period is 15 minutes (backtest header), so security(..., '15', open) is the
      chart's own open series; the bar's open is known at its start.
    * highest / lowest include the current bar (Pine).
    * strategy.entry reverses: REVERSAL INTENDED (the source has no other exit).
    * FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders on the chart's own series.
    2 generic: PASS, bar counts only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427071_open_channel_cross"
FAMILY = "donchian_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "channel": [60, 30],
    "fast": [30, 20],
    "slow": [60, 90],
}
DEFAULT_PARAMS = {"channel": 60, "smooth": 60, "fast": 30, "slow": 60}


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
    sig = bars_df["open"]
    n, s = int(p["channel"]), int(p["smooth"])
    h = sig.rolling(n).max().ewm(span=s, adjust=False).mean()
    lo = sig.rolling(n).min().ewm(span=s, adjust=False).mean()
    hf, hs = h.rolling(int(p["fast"])).mean(), h.rolling(int(p["slow"])).mean()
    lf, ls = lo.rolling(int(p["fast"])).mean(), lo.rolling(int(p["slow"])).mean()
    long_c = ((hf < hs) & (hf.shift(1) >= hs.shift(1))).to_numpy()
    short_c = ((lf > ls) & (lf.shift(1) <= ls.shift(1))).to_numpy()
    m = len(sig)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
