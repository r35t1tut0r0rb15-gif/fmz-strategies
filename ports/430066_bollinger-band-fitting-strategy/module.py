"""Noro's Wizard v1.1, 1-hour bars, long only: a low under the lower Bollinger band of the lows (40, 2) with a 7-bar fast
RSI under 30 goes long; a green bar with a body above half its 10-bar average closes it. Adds are not ported.
Port of FMZ strategy #430066 "Bollinger Band Fitting Strategy" (Noro's Wizard Strategy v1.1).

FMZ source id: 430066

Source
    https://www.fmz.com/strategy/430066 (PineScript v2, FMZ last modified 2023-10-24 16:52:52).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 181-235), BB 40 / 2 on lows, fast RSI 7 under 30, body and colour filters off, pyramiding 10
    lower = sma(low, 40) - 2 stdev(low, 40); fastrsi = RSI of close from rma(.., 7)
    up1 = low < lower and fastrsi < 30 -> (close a short) entry long (lot fixed at the first entry)
    exit = close > open and |close - open| > sma(|close - open|, 10) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 10: each further signal while long adds a lot in the source. Adds are not ported
      (one net position). No short is ever opened (the close of a short never applies).
    * close_all acts on the position held at the start of the bar: a bar that both signals and
      closes ends flat when already long, and long when flat (the exit has nothing to close yet).
    * stdev is the population deviation; rma is Wilder's average. The 1900-2100 window is the
      author's backtest window: dropped. Long only; Opposite entries cannot occur.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, Bollinger bands, an RSI and body ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital % lot and pyramiding 10 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430066 (2 members, best partner #432786, Jaccard 0.714); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430066_noro_wizard_v11"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [40, 20],
    "rsi_limit": [30, 20],
}
DEFAULT_PARAMS = {"length": 40, "mult": 2.0, "rsi_len": 7, "rsi_limit": 30, "body_len": 10}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    lower = lo.rolling(n).mean() - p["mult"] * lo.rolling(n).std(ddof=0)
    up1 = ((lo < lower) & (_fast_rsi(c, int(p["rsi_len"])) < p["rsi_limit"])).to_numpy()
    body = (c - o).abs()
    ex = ((c > o) & (body > body.rolling(int(p["body_len"])).mean() / 2)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up1[i]:
            pos = 1
        if ex[i] and start == 1:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
