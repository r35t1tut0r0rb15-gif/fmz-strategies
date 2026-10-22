"""SMA 74 / 70 crossings, 4-hour bars, entries only from flat: the cross up goes long, the cross down goes short, each with a 353-point stop and a 1059-point target from the entry price.
Port of FMZ strategy #482437 "Adaptive Trend Following Strategy Based on Moving Average Crossover" (Bitcoin Strategy by Jag).

FMZ source id: 482437

Source
    https://www.fmz.com/strategy/482437 (PineScript v5, FMZ last modified 2025-02-18 14:23:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 77-135), SMA 74 / 70; stop offset 353 USD, target 3 x 353; trade size 1
    flat and crossover(sma74, sma70) -> entry Long (1);  flat and crossunder -> entry Short;  long: exit(stop = avg - 353, limit = avg + 1059);  short: exit(stop = avg + 353, limit = avg - 1059)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing" offset is a fixed stop from the average price, a price amount, ported as a fraction
      of 42000 (8.40e-03, target 2.52e-02) of the entry fill, active from the fill (as #440797).
      Entries need a flat position at the bar's close, so a loop follows the bracket on each bar's high /
      low (as #449508) to know when the position is flat. Opposite entries cannot occur (entries only from
      flat). Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. The trade size is sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; point bracket as fractions of the fill.
    2 generic: PASS, SMA crossings with a point bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: trade size 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482437_sma74_70_cross_point_bracket_flat_only"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [74, 20],
    "long_len": [70, 50],
}
DEFAULT_PARAMS = {"short_len": 74, "long_len": 70, "sl_frac": 8.40476e-03, "tp_frac": 2.52143e-02}


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
    a = c.rolling(int(p["short_len"])).mean()
    b = c.rolling(int(p["long_len"])).mean()
    lc = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    sc = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    sl, tp = float(p["sl_frac"]), float(p["tp_frac"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg = 0, 0, np.nan
    for i in range(m):
        if pend != 0:
            pos, pend, avg = pend, 0, ov[i]
        if pos == 1 and (lv[i] <= avg * (1 - sl) or hv[i] >= avg * (1 + tp)):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= avg * (1 + sl) or lv[i] <= avg * (1 - tp)):
            pos = 0
        if pos == 0 and lc[i]:
            le[i], pend = True, 1
        elif pos == 0 and sc[i]:
            se[i], pend = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
