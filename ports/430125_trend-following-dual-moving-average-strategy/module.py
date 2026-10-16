"""ADXR (HPotter), 45-minute bars: the average of ADX 14 and its value 14 bars back under 13 holds a long (a quiet market),
above 45 holds a short.
Port of FMZ strategy #430125 "Trend Following Dual Moving Average Strategy" (Average Directional Movement Index Rating Backtest).

FMZ source id: 430125

Source
    https://www.fmz.com/strategy/430125 (PineScript v2, FMZ last modified 2023-10-25 11:42:23).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 144-189), ADX 14, ADXR 14, signals 13 / 45
    xADX = 100 x rma(|DI+ - DI-| / (DI+ + DI-), 14) (Wilder DI 14); xADXR = (xADX + xADX[14]) / 2
    xADXR < 13 -> entry long;  xADXR > 45 -> entry short;  else pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * ADX as the source's fADX (Wilder averages; fixnan carries the last DI value over a zero true
      range). "Trade reverse" defaults to false and is fixed.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_430125_adxr_levels"
FAMILY = "directional_movement"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_adx": [14, 28],
    "signal1": [13, 20],
}
DEFAULT_PARAMS = {"length_adx": 14, "signal1": 13, "signal2": 45}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    return x.ewm(alpha=1 / n, adjust=False).mean()


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _adx(h, lo, c, n):
    up, down = h.diff(), -lo.diff()
    plus_dm = ((up > down) & (up > 0)).astype(float) * up.fillna(0.0)
    minus_dm = ((down > up) & (down > 0)).astype(float) * down.fillna(0.0)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n).replace(0.0, np.nan)
    plus = _fixnan(100 * _rma(plus_dm, n) / atr)
    minus = _fixnan(100 * _rma(minus_dm, n) / atr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)


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
    n = int(p["length_adx"])
    adx = _adx(bars_df["high"], bars_df["low"], bars_df["close"], n)
    adxr = ((adx + adx.shift(n)) / 2).to_numpy()
    m = len(adxr)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if adxr[i] < p["signal1"]:
            pos = 1
        elif adxr[i] > p["signal2"]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
