"""Noro's fast RSI robot, 5-minute bars: four red bars in a row with RSI 7 under 25 and a real body (from flat or below the
entry price) go long, four green bars with RSI over 75 go short; a bar in the position's favour with RSI back inside
25-75 and a body over half the average closes everything. Adds are not ported.
Port of FMZ strategy #431924 "基于快速RSI的风控复合交易策略Fast-RSI-Risk-Control-Compound-Futures-Trading-Strategy" (Robot BitMEX Fast RSI v1.0).

FMZ source id: 431924

Source
    https://www.fmz.com/strategy/431924 (PineScript v2, FMZ last modified 2023-11-13 11:36:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-239), RSI 7 / 25, open colour bars 4, body 20 % / 50 %, martingale on, pyramiding 10
    up = 4 red bars and rsi < 25 and body >= 20 % of sma(body, 10) and (flat or close < avg price) -> entry long
    dn = 4 green bars and rsi > 75 and body ok and (flat or close > avg price) -> entry short
    exit = position and the bar in its favour and 25 < rsi < 75 and body >= 50 % of sma(body, 10) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * RSI as written (Wilder rma, 0 / 100 edge cases). pyramiding 10: adds are not ported (one net
      position), so the average price is the first entry's fill (the open after the signal). The
      martingale doubles the lot after a loss: sizing, stored.
    * A close_all written after an entry acts on the position held at the bar's start and leaves the
      bar flat (C31-C39 convention). Entries reverse: REVERSAL INTENDED. FREQ = "5min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, RSI levels and bar colour / body filters.
    3 crypto-exchange-only: no (exchange pair in the header only (BitMEX in the title only)).
    4 signals only: the capital % lot with the martingale multiplier stored in original_sizing.txt.
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

NAME = "fmz_431924_noro_fast_rsi_robot"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "limit": [25, 15],
    "open_bars": [4, 2],
}
DEFAULT_PARAMS = {"rsi_len": 7, "limit": 25, "open_bars": 4, "open_body": 20, "close_body": 50}


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
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    body = (c - o).abs()
    ab = body.rolling(10).mean()
    ob = (body >= ab / 100 * p["open_body"]).to_numpy()
    cb = (body >= ab / 100 * p["close_body"]).to_numpy()
    k = int(p["open_bars"])
    g = (c > o).astype(float)
    rd = (c < o).astype(float)
    four_g = (g.rolling(k).mean() == 1).to_numpy()
    four_r = (rd.rolling(k).mean() == 1).to_numpy()
    bar = np.sign((c - o).to_numpy())
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lo_, hi_ = float(p["limit"]), 100 - float(p["limit"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg = 0, np.nan
    for i in range(m):
        start = pos
        up = four_r[i] and r[i] < lo_ and ob[i] and (start == 0 or cv[i] < avg)
        dn = four_g[i] and r[i] > hi_ and ob[i] and (start == 0 or cv[i] > avg)
        norma = lo_ < r[i] < hi_
        ex = ((start == 1 and bar[i] == 1) or (start == -1 and bar[i] == -1)) and norma and cb[i]
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
