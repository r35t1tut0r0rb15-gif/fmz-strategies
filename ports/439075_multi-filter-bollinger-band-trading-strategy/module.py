"""Noro's Bollinger dip buys, 1-hour bars, long only: from flat, a red bar with a large body closing at or under the lower band (SMA 20 of ohlc4 - 1 sigma) with the fast RSI 7 under 30 buys; an upper-band
green bar with the fast RSI over 70, or any large-bodied green bar, closes the long.
Port of FMZ strategy #439075 "Multi filter Bollinger Band Trading Strategy" (Bollinger str 1.4).

FMZ source id: 439075

Source
    https://www.fmz.com/strategy/439075 (PineScript v3, FMZ last modified 2024-01-17 15:12:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 152-213), long on, short off; BB 20 x 1 on ohlc4; body, colour and RSI filters on; date window 1900-2100
    up = close <= lower and red and body > sma(body, 10) / 2 and fast rsi < 30 and (close < avg price or flat) -> entry Long;  dn = close >= upper and green and body and fast rsi > 70 and (close > avg or flat) -> entry Short (qty 0)
    exit = (long and green or short and red) and body -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Shorts are off: the short entry has quantity 0 and only closes an open long (Noro's idiom; as
      #435019). The "close under the average price" add is blocked by the default pyramiding (one
      entry). The fast RSI uses rma(7) of the gains and losses (down == 0 -> 100, up == 0 -> 0). stdev is
      the population deviation. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands, bar colour, body and a fast RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439075_noro_bollinger_dip_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    n = int(p["length"])
    basis = src.rolling(n).mean()
    dev = float(p["mult"]) * src.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    nbody = (c - o).abs()
    body = (nbody > nbody.rolling(10).mean() / 2).to_numpy()
    d = c.diff()
    fu, fd = _rma(d.clip(lower=0), 7), _rma((-d).clip(lower=0), 7)
    with np.errstate(divide="ignore", invalid="ignore"):
        rsi = 100.0 - 100.0 / (1.0 + fu / fd)
    rsi = rsi.where(fu != 0, 0.0).where(fd != 0, 100.0)
    rsi = rsi.where(fd.notna() & (fu.notna() | (fd == 0)))
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    up = (c <= lower).to_numpy() & red & body & (rsi < 30).to_numpy()
    dn = (c >= upper).to_numpy() & green & body & (rsi > 70).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and (dn[i] or (green[i] and body[i])):
            lx[i], pos = True, 0
        elif pos == 0 and up[i] and i + 1 < m:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
