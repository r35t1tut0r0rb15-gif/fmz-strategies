"""Keltner band touches of the open, 5-minute bars: the bar's open crossing the lower band (SMA 20 of opens minus 4 x the SMA 20 true range) in either direction goes long, crossing the upper band in either
direction goes short; reversing.
Port of FMZ strategy #437490 "Sideways Breakthrough Oscillation Strategy" (Seitwärtsdoppelpenetration).

FMZ source id: 437490

Source
    https://www.fmz.com/strategy/437490 (PineScript v3, FMZ last modified 2024-01-03 11:29:24).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 151-180), source open, true range on, length 20, mult 4
    ma = sma(open, 20);  rangema = sma(tr, 20);  upper / lower = ma +- 4 rangema
    cross(lower, open) -> entry buyEntry;  cross(open, upper) -> entry sellEntry;  close buyEntry on cross(open, upper);  close sellEntry on cross(lower, open)

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is a crossing in either direction. The closes repeat the opposite entry conditions, so each
      crossing reverses (call order: entries, then closes of the position open at the bar's close). tr is
      na on the first bar (Pine v3). REVERSAL INTENDED. No sizing code. FREQ = "5min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR-width channel.
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

NAME = "fmz_437490_keltner_open_band_cross"
FAMILY = "mean_reversion"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [4.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 4.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _cross(a, b):
    a1, b1 = a.shift(1), b.shift(1)
    return ((a > b) & (a1 <= b1)) | ((a < b) & (a1 >= b1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    ma = o.rolling(n).mean()
    rm = tr.rolling(n).mean()
    upper, lower = ma + rm * float(p["mult"]), ma - rm * float(p["mult"])
    buy = _cross(lower, o).to_numpy()
    sell = _cross(o, upper).to_numpy()
    m = len(o)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and sell[i]:
                new = 0
            elif pos == -1 and buy[i]:
                new = 0
        if new == 1 and pos != 1:
            le[i] = True
        elif new == -1 and pos != -1:
            se[i] = True
        elif new == 0 and pos == 1:
            lx[i] = True
        elif new == 0 and pos == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
