"""SMA 50 / 200 golden crosses above a CMO-weighted EMA, 1-hour bars, long only: the SMA 50 crossing over the SMA 200 with the close above the VAR line goes long; a death cross or a close under the VAR line
closes.
Port of FMZ strategy #443096 "Dual Moving Average Volatility Tracking Strategy" (GCC-PTT (Combined Golden Cross and Progressive Trend Tracker)).

FMZ source id: 443096

Source
    https://www.fmz.com/strategy/443096 (PineScript v5, FMZ last modified 2024-02-29 11:15:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-183), SMA 50 / 200; VAR = ema(close x |CMO(14)|, 14); BB 20 / 2 (plots only)
    VAR = ema(src x abs((sum up 14 - sum down 14) / (sum up + sum down)), 14);  crossover(sma50, sma200) and close > VAR -> entry;  crossunder or close < VAR -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The VAR line is the EMA of the close weighted by the absolute 14-bar CMO, as written (it sits far
      under the price). The bands only plot. Long only. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, golden crosses with a CMO-weighted line.
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

NAME = "fmz_443096_golden_cross_cmo_var_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200, "var_len": 14}


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
    n = int(p["var_len"])
    d = c.diff()
    ud = d.clip(lower=0).rolling(n).sum()
    dd = (-d).clip(lower=0).rolling(n).sum()
    cmo = (ud - dd) / (ud + dd).where((ud + dd) != 0)
    var = (c * cmo.abs()).ewm(span=n, adjust=False, ignore_na=True).mean()
    gx = (f > s) & (f.shift(1) <= s.shift(1))
    dx = (f < s) & (f.shift(1) >= s.shift(1))
    go = (gx & (c > var)).to_numpy()
    out = (dx | (c < var)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
