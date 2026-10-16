"""Noro's TrendMaster, 3-hour bars: the trend is up once two lows sit above the 21-bar close channel's
midpoint and down once two highs sit below it; in an up trend a bar with a real body and a fast RSI(2)
under 60 goes long, in a down trend a real-bodied bar with RSI(2) over 40 goes short.
Port of FMZ strategy #427814 "Trend Following Strategy" (Noro's TrendMaster v1.0).

FMZ source id: 427814

Source
    https://www.fmz.com/strategy/427814 (PineScript v2, FMZ last modified 2023-09-25 17:50:11).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 220-276), channel 21 of closes, RSI 2, body vs SMA 10
    center = (highest(close, 21) + lowest(close, 21)) / 2
    trend = low > center and low[1] > center[1] ? 1 : high < center and high[1] < center[1] ? -1 : trend[1]
    body = |close - open| > sma(|close - open|, 10) / 2
    up = trend == 1 and rsi2 < 60 and (avg price > close or not long) and body -> entry long
    dn = trend == -1 and rsi2 > 40 and (avg price < close or not short) and body -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 0: an entry on the side already held is ignored, so the average-price clause only
      matters for adds; the port enters when not on that side (the clause is true then).
    * The long / short switches default on (qty 0 when off: Noro's idiom, not searched); the date
      window is dropped. trend[1] is na before the first defining bar.
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel of closes, RSI levels, body ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the switch quantities stored in original_sizing.txt.
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

NAME = "fmz_427814_noro_trendmaster"
FAMILY = "channel_trend_pullback"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [21, 10, 50, 100],
}
DEFAULT_PARAMS = {"len": 21, "rsi_len": 2, "body_len": 10}


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
    n = int(p["len"])
    center = (c.rolling(n).max() + c.rolling(n).min()) / 2
    t_up = ((lo > center) & (lo.shift(1) > center.shift(1))).to_numpy()
    t_dn = ((h < center) & (h.shift(1) < center.shift(1))).to_numpy()
    d = c.diff()
    k = int(p["rsi_len"])
    fu, fd = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + fu / fd)).where(fu != 0, 0.0).where(fd != 0, 100.0).where(fu.notna() & fd.notna())
    nb = (c - o).abs()
    body = (nb > nb.rolling(int(p["body_len"])).mean() / 2).to_numpy()
    rv = rsi.to_numpy()
    m = len(rv)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos = 0, 0
    for i in range(m):
        if t_up[i]:
            trend = 1
        elif t_dn[i]:
            trend = -1
        if trend == 1 and rv[i] < 60 and body[i] and pos != 1:
            pos = 1
        elif trend == -1 and rv[i] > 40 and body[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
