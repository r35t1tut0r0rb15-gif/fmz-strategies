"""WaveTrend (10, 21, double-smoothed) level crossings with an SMA 500 trend, daily bars: the line crossing over -45 above the SMA goes long, crossing under 45 below it goes short; the cross under 45 closes a long, the cross over -45 closes a short; reversing.
Port of FMZ strategy #475624 "Dynamic Wave Trend Tracking Strategy" (WaveTrend Trend).

FMZ source id: 475624

Source
    https://www.fmz.com/strategy/475624 (PineScript v6, FMZ last modified 2024-12-20 16:17:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-166), channel 10, average 21 (ci and tci both EMA 21); levels 45 / -45; trend SMA 500
    crossover(tci, -45) and close > sma500 -> entry Long;  crossunder(tci, 45) -> close Long;  crossunder(tci, 45) and close < sma500 -> entry Short;  crossover(tci, -45) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * tci is an EMA 21 of ci, itself an EMA 21 of the channel index, as written. A close coinciding with
      the opposite entry only repeats the reversal (#437773), so it is masked on entry bars. REVERSAL
      INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, WaveTrend level crossings with a trend filter.
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

NAME = "fmz_475624_wavetrend_45_cross_sma500_trend_reversal"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [500, 200],
    "level": [45, 60],
}
DEFAULT_PARAMS = {"ma_length": 500, "level": 45, "n1": 10, "n2": 21}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ap = (h + lo + c) / 3
    n1, n2 = int(p["n1"]), int(p["n2"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    k = (ap - esa) / (0.015 * d)
    tci = k.ewm(span=n2, adjust=False).mean().ewm(span=n2, adjust=False).mean()
    ma = c.rolling(int(p["ma_length"])).mean()
    lv = float(p["level"])
    cu = (tci > -lv) & (tci.shift(1) <= -lv)
    cd = (tci < lv) & (tci.shift(1) >= lv)
    le = cu & (c > ma)
    se = cd & (c < ma)
    return le, cd & ~se, se, cu & ~le


def portfolio_kwargs(**params):
    return {}
