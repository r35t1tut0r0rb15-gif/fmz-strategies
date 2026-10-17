"""Noro's Connors RSI with a fast RSI, 1-hour bars: a red bar of real body with both the Connors RSI and the fast RSI 7
under 25 (from flat or below the entry price) goes long, the mirror on a green bar goes short; a bar of real body in the
position's favour (green while long, red while short) closes everything. Adds are not ported.
Port of FMZ strategy #431401 "RSI动量反转策略RSI-Momentum-Reversal-Strategy" (Noro's Connors RSI Strategy v1.0).

FMZ source id: 431401

Source
    https://www.fmz.com/strategy/431401 (PineScript v2, FMZ last modified 2023-11-07 15:45:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 275-360), CRSI 3 / 2 / 100, fast RSI 7, limit 25, both modes, body and colour filters on, pyramiding 10
    crsi = (rsi(close, 3) + rsi(streak, 2) + count of the last 99 ROCs below the current one) / 3
    up = red bar and (flat or close < avg price) and crsi < 25 and fastrsi < 25 and body > sma(body, 10) / 3
    dn = green bar and (flat or close > avg price) and crsi > 75 and fastrsi > 75 and body
    up -> (close_all if short) entry long;  dn -> (close_all if long) entry short
    exit = (long and green bar or short and red bar) and body -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The CRSI is ported as written: the ROC count is a raw count of 99 (not a percentage), the streak
      without nz (an na streak stays na until a reset). pyramiding 10: adds are not ported (one net
      position), so the average price is the first entry's fill (the open after the signal).
    * A close_all written after an entry acts on the position held at the bar's start and leaves the
      bar flat (C31-C39 convention). Martingale off; the lot is sizing. Entries reverse: REVERSAL
      INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, RSI composites and bar colour / body filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, the lot formula and pyramiding 10 stored in original_sizing.txt.
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

NAME = "fmz_431401_connors_fast_rsi"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [25, 15],
    "fast_len": [7, 14],
}
DEFAULT_PARAMS = {"limit": 25, "fast_len": 7, "rsi_len": 3, "streak_len": 2, "lookback": 100}


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


def _streak(c):
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(1, m):
        if cv[i] > cv[i - 1]:
            up[i] = up[i - 1] + 1
        else:
            up[i] = 0.0
        if cv[i] < cv[i - 1]:
            dn[i] = dn[i - 1] - 1
        else:
            dn[i] = 0.0
    return pd.Series(up + dn, index=c.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    srsi = _rsi(_streak(c).dropna(), int(p["streak_len"])).reindex(c.index)
    roc = c / c.shift(1) - 1
    lb = int(p["lookback"])
    rv = roc.to_numpy(dtype=float)
    m = len(rv)
    cnt = np.zeros(m)
    for i in range(m):
        lo_ = max(0, i - lb + 1)
        past = rv[lo_:i]
        cnt[i] = np.sum(past < rv[i]) if not np.isnan(rv[i]) else 0
    crsi = ((rsi + srsi).to_numpy() + cnt) / 3
    frsi = _rsi(c, int(p["fast_len"])).to_numpy()
    body = (c - o).abs()
    bod = (body > body.rolling(10).mean() / 3).to_numpy()
    bar = np.sign((c - o).to_numpy())
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lim = float(p["limit"])
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg = 0, np.nan
    for i in range(m):
        start = pos
        up = (bar[i] == -1 and (start == 0 or cv[i] < avg) and crsi[i] < lim and frsi[i] < lim and bod[i])
        dn = (bar[i] == 1 and (start == 0 or cv[i] > avg) and crsi[i] > 100 - lim and frsi[i] > 100 - lim
              and bod[i])
        ex = ((start == 1 and bar[i] == 1) or (start == -1 and bar[i] == -1)) and bod[i]
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
