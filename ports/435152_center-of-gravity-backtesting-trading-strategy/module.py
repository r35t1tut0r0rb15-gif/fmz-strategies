"""HPotter centre-of-gravity bands, 1-hour bars: the 20-bar linear regression of the close evaluated 5 bars back, plus and
minus 1 % of the close, gives the bands; a close above the upper band goes long, below the lower band goes short; held in
between and reversed on the opposite break.
Port of FMZ strategy #435152 "Center of Gravity Backtesting Trading Strategy" (Center Of Gravity Backtest).

FMZ source id: 435152

Source
    https://www.fmz.com/strategy/435152 (PineScript v2, FMZ last modified 2023-12-12 16:56:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 135-155), length 20, offset m 5, percent 1, signal line 1; reverse false
    lg = linreg(close, 20, 5);  r1 = lg + close x 1 %;  s1 = lg - close x 1 %;  pos = close > r1 ? 1 : close < s1 ? -1 : pos[1]

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(src, n, m) is the least-squares line of the last n closes evaluated at n - 1 - m (m bars
      before the newest point), as Pine defines it. strategy.entry reverses: REVERSAL INTENDED. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a regression line with percent bands.
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

NAME = "fmz_435152_center_of_gravity_bands"
FAMILY = "mean_reversion_band"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "percent": [1.0, 0.5],
}
DEFAULT_PARAMS = {"length": 20, "m": 5, "percent": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _linreg(v, n, off):
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        x = np.arange(n, dtype=float)
        xm = x.mean()
        w = (x - xm) / ((x - xm) ** 2).sum()
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        slope = win @ w
        icpt = win.mean(axis=1) - slope * xm
        out[n - 1:] = icpt + slope * (n - 1 - off)
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    cv = bars_df["close"].to_numpy(dtype=float)
    lg = _linreg(cv, int(p["length"]), int(p["m"]))
    band = cv * float(p["percent"]) / 100
    with np.errstate(invalid="ignore"):
        up, dn = cv > lg + band, cv < lg - band
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
