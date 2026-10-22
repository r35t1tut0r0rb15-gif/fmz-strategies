"""Pullbacks into strong green candles above a sloped EMA 44, daily bars, long only: after a green candle closing over the high before it and over the EMA, a bar trading through that candle's 50 % close-to-low level buys (from flat, the EMA rising or falling enough); a long sells after a red candle or a low under the previous low.
Port of FMZ strategy #468320 "高斯交叉EMA趋势滑点追踪策略-Gaussian-Cross-EMA-Trend-Retracement-Strategy" (Custom Strategy with EMA and Candle Conditions).

FMZ source id: 468320

Source
    https://www.fmz.com/strategy/468320 (PineScript v5, FMZ last modified 2024-09-26 15:34:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-207), EMA 44; slope = EMA 44 minus the EMA 44 of close[9], threshold 0.5 (price units); retrace 50 % of the previous close-to-low; one trade at a time
    close[1] > high[2] and green[1] and close[1] > ema44 and low <= retrace <= high and |slope| > 0.5 and flat -> entry Buy
    long and (red[1] or low < low[1]) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.ema(close[9], 44) is the EMA 44 nine bars back, so the slope is ema44 - ema44[9]; the 0.5
      threshold is a price amount, ported as a fraction of 42000 of the close (1.19e-5). The wick /
      body test is computed but not part of the entry, as written. The retrace level and exits are as
      written; the entry needs a flat position at the bar's close
      and the exit a long held into the bar. The debugging labels are drawing only. Long only. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, strong-candle pullbacks with a sloped EMA filter.
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

NAME = "fmz_468320_strong_green_candle_half_retrace_ema44_slope_long"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [44, 21],
    "flat_frac": [0.0000119, 0.001],
}
DEFAULT_PARAMS = {"ema_len": 44, "flat_frac": 0.0000119}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    inclined = (e - e.shift(9)).abs() > float(p["flat_frac"]) * c
    o1, l1, c1 = o.shift(1), lo.shift(1), c.shift(1)
    retrace = c1 - (c1 - l1) * 0.5
    go = ((c1 > h.shift(2)) & (c1 > o1) & (c1 > e) & (lo <= retrace) & (h >= retrace) & inclined).to_numpy()
    out = ((c1 < o1) | (lo < l1)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if go[i] and pos == 0:
            le[i], pos = True, 1
        elif out[i] and pos == 1:
            lx[i], pos = True, 0                 # the close acts only on a long held into the bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
