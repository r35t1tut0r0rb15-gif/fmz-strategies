"""Noro's MA tests: a trend state flips to up when a whole bar (its low) is above a moving average
and to down when a whole bar (its high) is below it; a flip to up goes long, a flip to down goes
short. The average is one of seven types (default: SMA 30 of the close).
Port of FMZ strategy #427090 "Dual Moving Average Crossover Strategy".

FMZ source id: 427090

Source
    https://www.fmz.com/strategy/427090 (PineScript v2, FMZ last modified 2023-09-17 22:35:07).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 118-162), MA length 30, type 1 (SMA), source close
    ma = type 1 sma | 2 ema | 3 vwma | 4 dema | 5 tema | 6 kama | 7 (highest + lowest) / 2
    trend = low > ma ? 1 : high < ma ? -1 : trend[1]
    trend == 1 and trend[1] == -1 -> entry long; trend == -1 and trend[1] == 1 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * `ma_type` is the source's "Type" input. Type 3 (vwma) weights by volume and is not ported
      (check 8 / rule 8: volume users are held); the other six are, the grid tries three.
    * KAMA as written: kama = nz(kama[1]) + nsmooth x (src - nz(kama[1])), so it starts from 0 at
      the first bar with an efficiency ratio and converges (kept, not re-seeded).
    * trend[1] is na before the first state; a flip needs a defined previous state.
    * strategy.entry reverses: REVERSAL INTENDED (the source has no other exit).
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity per trade (sizing) stored in original_sizing.txt.
    5 ranges declared: GRID below (9 trials), before any backtest.
    6 near-duplicates: ND427090 (with #436514, Jaccard 0.789); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8); the vwma type is excluded.
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427090_noro_ma_trend_flip"
FAMILY = "ma_trend"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30, 50],
    "ma_type": [1, 2, 6],
}
DEFAULT_PARAMS = {"length": 30, "ma_type": 1}
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
    ma = _ma(bars_df["close"], int(p["length"]), int(p["ma_type"])).to_numpy()
    lo, hi = bars_df["low"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    m = len(ma)
    trend = np.zeros(m, dtype=np.int8)        # 0 = na
    for i in range(m):
        if lo[i] > ma[i]:
            trend[i] = 1
        elif hi[i] < ma[i]:
            trend[i] = -1
        else:
            trend[i] = trend[i - 1] if i else 0
    prev = np.concatenate(([0], trend[:-1]))
    long_c = (trend == 1) & (prev == -1)
    short_c = (trend == -1) & (prev == 1)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i]:
            pos = 1
        elif short_c[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
