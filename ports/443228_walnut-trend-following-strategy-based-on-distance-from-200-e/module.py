"""Stretches from an EMA 200, 3-hour bars: from flat, the close 0.75 % or more under the EMA after a down close goes long, 0.75 % or more over it after an up close goes short; the exit test includes
time_close(), always true, so each position closes after its first bar.
Port of FMZ strategy #443228 "Walnut Trend Following Strategy Based on Distance from 200 EMA" (Intraday Price Away from 200 EMA Strategy).

FMZ source id: 443228

Source
    https://www.fmz.com/strategy/443228 (PineScript v4, FMZ last modified 2024-03-01 10:50:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-206), EMA 200; threshold 0.75 %
    opentrades == 0: buy = close < ema and |distance %| >= 0.75 and close[1] < close[2] -> entry Buy;  sell mirrored -> entry Sell
    exit_buy = close >= ema or time_close(timeframe.period) or avg x 1.5 <= close -> close Buy;  exit_sell = close <= ema or time_close(...) or avg x 1.5 >= close -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * time_close(timeframe.period) is the bar's close time, a non-na number read as true, so both exit
      tests hold on every bar: each position closes at the end of its first bar (one-bar holds), as
      written. Entries need no open trade. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA stretch entries; one-bar holds as written.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443228_ema200_stretch_one_bar_hold"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [200, 100],
    "threshold": [0.75, 1.5],
}
DEFAULT_PARAMS = {"ema_period": 200, "threshold": 0.75}


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
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    dist = ((c - e) / e * 100).abs()
    th = float(p["threshold"])
    lg = ((c < e) & (dist >= th) & (c.shift(1) < c.shift(2))).to_numpy()
    sh = ((c > e) & (dist >= th) & (c.shift(1) > c.shift(2))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held = 0
    for i in range(m):
        if held == 1:
            lx[i], held = True, 0
        elif held == -1:
            sx[i], held = True, 0
        elif lg[i]:
            le[i], held = True, 1
        elif sh[i]:
            se[i], held = True, -1
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
