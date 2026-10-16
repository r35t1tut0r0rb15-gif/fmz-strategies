"""TEMA cross micro-profit, long only: TEMA 5 crossing above its SMA 3 while below the smoothed MA 30
goes long; TEMA crossing back under its SMA closes the long, but only once the close is at least 2 %
above the entry price.
Port of FMZ strategy #427372 "Renko Boxes and TEMA Indicator Micro-Profit Strategy".

FMZ source id: 427372

Source
    https://www.fmz.com/strategy/427372 (PineScript v2, FMZ last modified 2023-09-20 14:36:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 152-184), TEMA 5, SMA 3, SMMA 30, min gain 2 %, protections on
    long = crossover(tema, sma(tema, 3)) and tema < smma(close, 30) [and close <= avg price when in a position]
    crossunder(tema, sma(tema, 3)) and close >= 1.02 x avg price -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 100 with the "average protection" (adds only below the average price) is
      sizing (criterion 4, stored); the port holds one position, so the average price is the entry
      fill (the next open). With adds the average would sit lower and the 2 % exit come sooner.
    * The time filter (after 2017-09-22) is the author's backtest window: dropped.
    * "Renko" is only in the description: the code reads ordinary 1-hour bars.
    * smma = Wilder smoothing seeded with the SMA (as the script's own function).
    * Long only; entries only from flat; one signal per bar.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the gain test is on the close.
    2 generic: PASS, MA lengths and a percent of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 100, qty 1 and commission stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND427372 (with #439823, Jaccard 0.740); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427372_tema_cross_micro_profit_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tema_length": [5, 9],
    "smma_length": [30, 60],
    "min_gain_pct": [2.0, 1.0],
}
DEFAULT_PARAMS = {"tema_length": 5, "sma_length": 3, "smma_length": 30, "min_gain_pct": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """The script's smma: SMA seed, then (prev x (n - 1) + x) / n."""
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
    c = bars_df["close"]
    n = int(p["tema_length"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    tema = 3 * e1 - 3 * e2 + e2.ewm(span=n, adjust=False).mean()
    sm = tema.rolling(int(p["sma_length"])).mean()
    smma = _rma(c, int(p["smma_length"]))
    entry = ((tema > sm) & (tema.shift(1) <= sm.shift(1)) & (tema < smma)).to_numpy()
    xdown = ((tema < sm) & (tema.shift(1) >= sm.shift(1))).to_numpy()
    ov, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    gain = 1 + p["min_gain_pct"] / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, avg = 0, False, np.nan
    for i in range(m):
        if pending:
            pos, pending, avg = 1, False, ov[i]
        if pos == 1:
            if xdown[i] and cv[i] >= gain * avg:
                lx[i], pos = True, 0
        elif not pending and entry[i]:
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
