"""Parabolic SAR (0.02 / 0.02 / 0.2) crossings, 1-hour bars: the close crossing over the SAR goes long, crossing under goes short; reversing.
Port of FMZ strategy #439080 "Momentum Inversion Tracking Strategy" (PSAR).

FMZ source id: 439080

Source
    https://www.fmz.com/strategy/439080 (PineScript v5, FMZ last modified 2024-01-17 15:46:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 128-144), start 0.02, increment 0.02, maximum 0.2; 10 % of equity
    sar = sar(0.02, 0.02, 0.2);  crossover(close, sar) -> entry Long;  crossunder(close, sar) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SAR follows Pine's documented ta.sar algorithm (first trend from the first two closes; the SAR
      never inside the last two bars' range). strategy.entry reverses: REVERSAL INTENDED. The 10 % of
      equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / SAR crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_439080_psar_close_cross"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "increment": [0.02, 0.01],
    "maximum": [0.2, 0.1],
}
DEFAULT_PARAMS = {"increment": 0.02, "maximum": 0.2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    inc = float(p["increment"])
    sar = pd.Series(_sar(hv, lv, cv, inc, inc, float(p["maximum"])), index=bars_df.index)
    c = bars_df["close"]
    up = (c > sar) & (c.shift(1) <= sar.shift(1))
    dn = (c < sar) & (c.shift(1) >= sar.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
