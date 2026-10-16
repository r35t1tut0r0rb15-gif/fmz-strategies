"""Noro's Price Channel v1.1, 1-hour bars: above the centre of the 30-bar close channel, two red bars or a 2-bar fast RSI
under 25 go long; below it, two green bars or the fast RSI over 75 go short; a bar against the position (green for a
long, red for a short) with a body above half its 10-bar average closes everything.
Port of FMZ strategy #430009 "Noros-值道策略v11Noros-Price-Channel-Strategy-v11" (Noro's Price Channel Strategy v1.1).

FMZ source id: 430009

Source
    https://www.fmz.com/strategy/430009 (PineScript v2, FMZ last modified 2023-10-24 10:59:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 176-237), price channel 30, color and RSI rules on, leverage 1
    center = (highest(close, 30) + lowest(close, 30)) / 2
    fastrsi = RSI of close from rma(up moves, 2) / rma(down moves, 2)
    up1 = two red bars and close > center; up2 = fastrsi < 25 and close > center   -> (close a short) entry long
    dn1 = two green bars and close < center; dn2 = fastrsi > 75 and close < center -> (close a long) entry short
    exit = ((long and close > open) or (short and close < open)) and body > sma(body, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel "trend" variable is computed but never used by any order: not ported.
    * The exit is tested on the position held at the start of the bar. When it fires on a bar that
      also signals an entry, the close_all written after the entry wins and the bar ends flat (both
      orders are filled at the next open; the source's order of statements is followed).
    * rma is Wilder's average (alpha 1 / n). The year / month / day window (1900-2100) is the author's
      backtest window: dropped. Leverage 1 is sizing (original_sizing.txt).
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a close channel, bar colours, body ratios and an RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: lot = equity / close x leverage stored in original_sizing.txt.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND430009 (2 members, best partner #433968, Jaccard 0.726); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430009_noro_price_channel_v11"
FAMILY = "channel_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pch": [30, 15, 60],
    "rsi_limit": [25, 15],
}
DEFAULT_PARAMS = {"pch": 30, "rsi_limit": 25, "rsi_len": 2, "body_len": 10}


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


def _fast_rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["pch"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    bar = np.sign(c - o)
    rbars = (bar == -1) & (bar.shift(1) == -1)
    gbars = (bar == 1) & (bar.shift(1) == 1)
    fr = _fast_rsi(c, int(p["rsi_len"]))
    lim = float(p["rsi_limit"])
    up = ((rbars | (fr < lim)) & (c > center)).to_numpy()
    dn = ((gbars | (fr > 100 - lim)) & (c < center)).to_numpy()
    body = (c - o).abs()
    big = (body > body.rolling(int(p["body_len"])).mean() / 2).to_numpy()
    bv = bar.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        if big[i] and ((start == 1 and bv[i] == 1) or (start == -1 and bv[i] == -1)):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
