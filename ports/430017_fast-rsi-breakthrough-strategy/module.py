"""Noro's Fast RSI v1.2, 3-hour bars: a red bar with a body above a quarter of its EMA 30 and a 7-bar fast RSI under 30
goes long (from flat, or below a short's entry price); the mirror goes short; a bar against the position with the RSI
back past the limit and a body above half the average closes everything. Adds are not ported.
Port of FMZ strategy #430017 "Fast RSI Breakthrough Strategy" (Noro's Fast RSI Strategy v1.2).

FMZ source id: 430017

Source
    https://www.fmz.com/strategy/430017 (PineScript v3, FMZ last modified 2023-10-24 11:51:56).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 183-231), RSI period 7, limit 30, RSI bars 1, pyramiding 5
    fastrsi = RSI of close from rma(up moves, 7) / rma(down moves, 7); emabody = ema(|close - open|, 30)
    up = red bar and (flat or close < avg price) and fastrsi < 30 and body > emabody / 4    -> entry long
    dn = green bar and (flat or close > avg price) and fastrsi > 70 and body > emabody / 4  -> entry short
    exit = ((long and fastrsi > 30 and green) or (short and fastrsi < 70 and red)) and body > emabody / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 5: a same-side signal below a long's (above a short's) average price adds a unit in
      the source. Adds are not ported (one net position); the average price stays the first fill (the
      next open after the signal). A signal against the position reverses it when the close is beyond
      the average price on the losing side, as written.
    * The exit is tested on the position held at the start of the bar; when it fires on a bar that
      also signals an entry, the close_all written after the entry wins and the bar ends flat.
    * rma is Wilder's average (alpha 1 / n). The 2018-2100 window is the author's backtest window:
      dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, RSI levels and body ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per entry and pyramiding 5 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND426509 (2 members, best partner #426509, Jaccard 0.656); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430017_noro_fast_rsi_v12"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [7, 14],
    "limit": [30, 20],
}
DEFAULT_PARAMS = {"rsi_period": 7, "limit": 30}


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
    fr = _fast_rsi(c, int(p["rsi_period"])).to_numpy()
    lim = float(p["limit"])
    body = (c - o).abs()
    eb = body.ewm(span=30, adjust=False).mean()
    q4 = (body > eb / 4).to_numpy()
    h2 = (body > eb / 2).to_numpy()
    bv = np.sign(c - o).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg, pending = 0, np.nan, False
    for i in range(m):
        if pending:                                  # the entry fills at this bar's open
            avg, pending = ov[i], False
        start = pos
        up = bv[i] == -1 and (start == 0 or cv[i] < avg) and fr[i] < lim and q4[i]
        dn = bv[i] == 1 and (start == 0 or cv[i] > avg) and fr[i] > 100 - lim and q4[i]
        new = start
        if up:
            new = 1
        elif dn:
            new = -1
        if h2[i] and ((start == 1 and fr[i] > lim and bv[i] == 1) or
                      (start == -1 and fr[i] < 100 - lim and bv[i] == -1)):
            new = 0
        if new != start:
            pending = new != 0
            avg = np.nan
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
