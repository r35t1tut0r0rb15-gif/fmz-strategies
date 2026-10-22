"""Smoothed Heikin-Ashi colour changes, one bar late, daily bars, long only: Heikin-Ashi candles built from EMA 10 prices and smoothed again by EMA 10; the bar after a change to green buys, the bar after a change to red sells.
Port of FMZ strategy #473354 "双重平滑平均线趋势跟踪策略-基于改良型平安江氏K线-Double-Smoothed-Moving-Average-Trend-Following-Strategy-Based-on-Modified-Heikin-Ashi" (Smoothed Heiken Ashi Strategy Long Only).

FMZ source id: 473354

Source
    https://www.fmz.com/strategy/473354 (PineScript v5, FMZ last modified 2024-11-29 15:03:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-155), EMA 10 of OHLC, smoothing EMA 10; start date input unused; 100 % of equity
    haclose = (o + h + l + c) / 4;  haopen := na(haopen[1]) ? (o + c) / 2 : (haopen[1] + haclose[1]) / 2;  col = ema(haopen) > ema(haclose) ? red : lime;  colorChange[1] and col[1] == lime -> entry Long;  colorChange[1] and col[1] == red -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * haopen is a recursion (a loop) seeded on the first bar; only the smoothed open and close set the
      colour. The signals read the change one bar back, as written. The start-date input feeds nothing
      (its use is commented out). Long only. The equity share is not ported. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed Heikin-Ashi colour changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_473354_smoothed_heikin_ashi_colour_change_delayed_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [10, 20],
    "len2": [10, 20],
}
DEFAULT_PARAMS = {"len": 10, "len2": 10}


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
    n, n2 = int(p["len"]), int(p["len2"])
    o, h, lo, c = (bars_df[k].ewm(span=n, adjust=False).mean() for k in ("open", "high", "low", "close"))
    hc = ((o + h + lo + c) / 4).to_numpy(dtype=float)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ho = np.full(len(hc), np.nan)
    for i in range(len(hc)):
        if i == 0 or np.isnan(ho[i - 1]):
            ho[i] = (ov[i] + cv[i]) / 2
        else:
            ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    ix = bars_df.index
    o2 = pd.Series(ho, index=ix).ewm(span=n2, adjust=False).mean()
    c2 = pd.Series(hc, index=ix).ewm(span=n2, adjust=False).mean()
    red = o2 > c2
    change = red != red.shift(1)
    change.iloc[:1] = False
    le = change.shift(1, fill_value=False) & ~red.shift(1, fill_value=True)
    lx = change.shift(1, fill_value=False) & red.shift(1, fill_value=False)
    false = pd.Series(False, index=ix)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
