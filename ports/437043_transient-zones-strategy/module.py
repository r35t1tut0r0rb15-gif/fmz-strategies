"""Noro's transient zones, 1-hour bars: a down candle making a new 10-bar low with a real body (over a third of the 10-bar average body) goes long, an up candle making a new 10-bar high goes short; a long closes on
an up candle with a real body, a short on a down candle; reversing.
Port of FMZ strategy #437043 "Transient Zones Strategy" (TZ str 1.0).

FMZ source id: 437043

Source
    https://www.fmz.com/strategy/437043 (PineScript v2, FMZ last modified 2023-12-29 17:03:27).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 165-237), H left 10, H right -1, colour filter on, body filter on; long and short on; date window 2018-2100
    central_bar_is_lowest = low <= lowest(10) (h_right = -1: the current bar), central_bar_is_highest = high >= highest(10);  body = |close - open| > sma(|close - open|, 10) / 3
    up1 = lowest and body and close < open -> close_all if short, entry long;  dn1 = highest and body and close > open -> close_all if long, entry Short;  exit = (long and close > open or short and close < open) and body -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * With h_right = -1 the "zone" is the current bar against the last 10 bars including itself. Orders
      follow the script's call order; a close only acts on the position open at the bar's close, so an
      entry signal and its own exit test on one bar leave the new side. The date window covers everything:
      dropped. The sample-period and plot inputs place no orders. REVERSAL INTENDED. The equity-based lot is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes and body ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot and capital % stored.
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

NAME = "fmz_437043_noro_transient_zones"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "h_left": [10, 20],
    "use_body": [True, False],
}
DEFAULT_PARAMS = {"h_left": 10, "use_body": True, "use_color": True, "body_len": 10}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["h_left"])
    lowest = (lo <= lo.rolling(n).min()).to_numpy()
    highest = (h >= h.rolling(n).max()).to_numpy()
    nbody = (c - o).abs()
    body = (nbody > nbody.rolling(int(p["body_len"])).mean() / 3).to_numpy() | (not p["use_body"])
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    col = not p["use_color"]
    up1 = lowest & body & (red | col)
    dn1 = highest & body & (green | col)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        ex = ((pos == 1 and green[i]) or (pos == -1 and red[i])) and body[i]
        new = pos
        if up1[i] and new != 1:
            new = 1
        if dn1[i] and new != -1:
            new = -1
        if new == pos and ex:
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
