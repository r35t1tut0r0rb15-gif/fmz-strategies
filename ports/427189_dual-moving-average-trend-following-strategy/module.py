"""Noro's Trend MAs v1.7: a trend state turns up when three bars' lows are above the slow line
(default: the 20-bar mid-channel of the close) and down when two bars' highs are below it; in an
up-trend a dip under the fast EMA 5 on two red bars goes long, in a down-trend a pop above it on
two green bars goes short.
Port of FMZ strategy #427189 "Dual Moving Average Trend Following Strategy".

FMZ source id: 427189

Source
    https://www.fmz.com/strategy/427189 (PineScript v2, FMZ last modified 2023-09-18 21:57:00).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 158-245), slow MA type 7 length 20, fast EMA 5 filter on,
bars 2, stops off, long and short on
    ma = type 1 sma | 2 ema | 3 vwma | 4 dema | 5 tema | 6 kama | 7 (highest + lowest) / 2
    trend = low > ma and low[1] > ma[1] and low[2] > ma[2] ? 1 : high < ma and high[1] < ma[1] ? -1 : trend[1]
    up = trend == 1 and low < ema(close, 5) and two red bars -> entry long
    dn = trend == -1 and high > ema(close, 5) and two green bars -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * "stops" is off by default, so the stop level stays na and strategy.exit places no stop.
    * `ma_type` is the "Type of Slow MA" input; type 3 (vwma) uses volume and is not ported
      (check 8 / rule 8). KAMA starts from 0 as written (nz(kama[1])).
    * strategy.entry reverses: REVERSAL INTENDED (no other exit).
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the (off) percent stop stored in original_sizing.txt.
    5 ranges declared: GRID below (9 trials), before any backtest.
    6 near-duplicates: ND427189 (with #440999, Jaccard 0.727); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the vwma type is excluded.
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427189_noro_trend_mas_v17"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
    "ma_type": [7, 1, 2],
}
DEFAULT_PARAMS = {"length": 20, "ma_type": 7, "fast_len": 5, "bars": 2, "use_fast": True}
MA_TYPES = (1, 2, 4, 5, 6, 7)   # 3 (vwma) uses volume: not ported


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _kama(src, n):
    s = src.to_numpy(dtype=float)
    noise = pd.Series(np.abs(np.diff(s, prepend=np.nan)), index=src.index).rolling(n).sum().to_numpy()
    signal = np.abs(s - src.shift(n).to_numpy())
    with np.errstate(divide="ignore", invalid="ignore"):
        er = np.where(noise != 0, signal / noise, 0.0)
    er[np.isnan(noise) | np.isnan(signal)] = np.nan
    sm = (er * (0.20 - 0.05) + 0.05) ** 2
    out = np.full(len(s), np.nan)
    prev = np.nan
    for i in range(len(s)):
        if not np.isnan(sm[i]):
            base = 0.0 if np.isnan(prev) else prev      # nz(kama[1])
            out[i] = base + sm[i] * (s[i] - base)
        prev = out[i]
    return pd.Series(out, index=src.index)


def _ma(src, n, t):
    if t == 1:
        return src.rolling(n).mean()
    if t == 2:
        return _ema(src, n)
    if t == 4:
        return 2 * _ema(src, n) - _ema(_ema(src, n), n)
    if t == 5:
        e1 = _ema(src, n)
        e2 = _ema(e1, n)
        return 3 * e1 - 3 * e2 + _ema(e2, n)
    if t == 6:
        return _kama(src, n)
    if t == 7:
        return (src.rolling(n).max() + src.rolling(n).min()) / 2
    raise ValueError(f"ma_type {t} not ported (choices {MA_TYPES})")


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
    ma = _ma(c, int(p["length"]), int(p["ma_type"]))
    fast = _ema(c, int(p["fast_len"]))
    up3 = ((lo > ma) & (lo.shift(1) > ma.shift(1)) & (lo.shift(2) > ma.shift(2))).to_numpy()
    dn2 = ((h < ma) & (h.shift(1) < ma.shift(1))).to_numpy()
    bar = np.sign(c - o).to_numpy()
    nb = int(p["bars"])
    red = np.ones(len(bar), dtype=bool)
    green = np.ones(len(bar), dtype=bool)
    for k in range(nb):
        bk = np.concatenate((np.zeros(k), bar[:len(bar) - k])) if k else bar
        red &= bk == -1
        green &= bk == 1
    use_fast = bool(p["use_fast"])
    below_fast = (lo < fast).to_numpy() | (not use_fast)
    above_fast = (h > fast).to_numpy() | (not use_fast)
    m = len(bar)
    tgt = np.zeros(m, dtype=np.int8)
    trend, pos = 0, 0
    for i in range(m):
        if up3[i]:
            trend = 1
        elif dn2[i]:
            trend = -1
        if trend == 1 and below_fast[i] and red[i] and pos != 1:
            pos = 1
        elif trend == -1 and above_fast[i] and green[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
