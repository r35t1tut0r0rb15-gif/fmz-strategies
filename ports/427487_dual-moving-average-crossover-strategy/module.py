"""SMA 14 / 28 cross with a minimum gain, long only: the fast SMA crossing above the slow one goes long;
crossing back under closes the long, but only once the close is at least 0.6 % above the entry price.
Port of FMZ strategy #427487 "Dual Moving Average Crossover Strategy".

FMZ source id: 427487

Source
    https://www.fmz.com/strategy/427487 (PineScript v2, FMZ last modified 2023-09-21 16:40:01).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 203-218), SMA 14 / 28, min gain 0.6 %, protections on
    crossover(sma14, sma28) [and close <= avg price when in a position] -> entry long
    crossunder(sma14, sma28) and close >= 1.006 x avg price -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line (pyramiding 50, cash qty) is commented out: Pine defaults apply
      (pyramiding 0), so the averaging-down add never fills; the average price is the entry fill
      (the next open).
    * Long only; entries only from flat; one signal per bar.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the gain test is on the close.
    2 generic: PASS, MA lengths and a percent of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out sizing line stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427487_sma_cross_min_gain_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [14, 7],
    "slow": [28, 56],
    "min_gain_pct": [0.6, 1.5],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 28, "min_gain_pct": 0.6}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    ov, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    gain = 1 + p["min_gain_pct"] / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, avg = 0, False, np.nan
    for i in range(m):
        if pending:
            pos, pending, avg = 1, False, ov[i]
        if pos == 1:
            if dn[i] and cv[i] >= gain * avg:
                lx[i], pos = True, 0
        elif not pending and up[i]:
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
