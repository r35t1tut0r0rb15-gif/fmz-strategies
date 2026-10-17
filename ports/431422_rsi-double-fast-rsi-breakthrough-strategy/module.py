"""Noro's double fast RSI, 15-minute bars: a red bar of real body with RSI 7 or RSI 14 under 25 (from flat or below the
entry price) goes long, the mirror on a green bar goes short; a strong bar in the position's favour with both RSIs back
inside 25-75 closes everything.
Port of FMZ strategy #431422 "快速RSI指标二次突破策略Double-Fast-RSI-Breakthrough-Strategy" (Noro's Fast RSI Strategy v2.0).

FMZ source id: 431422

Source
    https://www.fmz.com/strategy/431422 (PineScript v2, FMZ last modified 2023-11-07 16:56:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 168-246), RSI 7 / 14, limits 25, body filters 1/5 and 1/2 of the 10-bar average
    up = red bar and (flat or close < avg price) and (rsi7 < 25 or rsi14 < 25) and body > sma(body, 10) / 5
    dn = green bar and (flat or close > avg price) and (rsi7 > 75 or rsi14 > 75) and body > sma(body, 10) / 5
    exit = (long and green or short and red) and both RSIs inside 25-75 and body > sma(body, 10) / 2 -> close_all
    up -> (close_all if short) entry long;  dn -> (close_all if long) entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * RSI as written (Wilder rma, 0 / 100 edge cases). The average price is the entry fill (the open
      after the signal); pyramiding is the default 1. A close_all written after an entry acts on the
      position held at the bar's start and leaves the bar flat (C31-C39 convention). Martingale off;
      the lot is sizing. The 2018 start is dropped. Entries reverse: REVERSAL INTENDED.
      FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels and bar colour / body filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital % lot formula stored in original_sizing.txt.
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

NAME = "fmz_431422_noro_double_fast_rsi"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [25, 15],
    "rsi2_len": [14, 21],
}
DEFAULT_PARAMS = {"rsi1_len": 7, "rsi2_len": 14, "limit": 25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


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
    o, c = bars_df["open"], bars_df["close"]
    r1 = _rsi(c, int(p["rsi1_len"])).to_numpy()
    r2 = _rsi(c, int(p["rsi2_len"])).to_numpy()
    body = (c - o).abs()
    ab = body.rolling(10).mean()
    b5 = (body > ab / 5).to_numpy()
    b2 = (body > ab / 2).to_numpy()
    bar = np.sign((c - o).to_numpy())
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lo_, hi_ = float(p["limit"]), 100 - float(p["limit"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg = 0, np.nan
    for i in range(m):
        start = pos
        up = bar[i] == -1 and (start == 0 or cv[i] < avg) and (r1[i] < lo_ or r2[i] < lo_) and b5[i]
        dn = bar[i] == 1 and (start == 0 or cv[i] > avg) and (r1[i] > hi_ or r2[i] > hi_) and b5[i]
        norma = lo_ < r1[i] < hi_ and lo_ < r2[i] < hi_
        ex = ((start == 1 and bar[i] == 1) or (start == -1 and bar[i] == -1)) and norma and b2[i]
        if up:
            pos = 1
        if dn:
            pos = -1
        if ex:
            pos = 0
        if pos != start and pos != 0 and i + 1 < m:
            avg = ov[i + 1]
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
