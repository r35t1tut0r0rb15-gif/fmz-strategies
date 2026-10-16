"""Heikin Ashi colour change, broker days: an HA candle turning green goes long, turning red goes short.
Port of FMZ strategy #428797 "Heiken Ashi Bar Color Change Strategy" (Kozlod - Heikin-Ashi Bar Color Change Strategy).

FMZ source id: 428797

Source
    https://www.fmz.com/strategy/428797 (PineScript v3, FMZ last modified 2023-10-09 15:38:46).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 120-141), no inputs
    haclose = ohlc4; haopen = (haopen[1] + haclose[1]) / 2 (first: (open + close) / 2)
    turnGreen = haclose > haopen and haclose[1] <= haopen[1] -> entry long
    turnRed = haclose <= haopen and haclose[1] > haopen[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no inputs; criterion 5's declared starting variants: `confirm` 1 (as written)
      and 2 (the new colour held for two bars, the bar before them of the old colour).
    * strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428797_heikin_ashi_colour_change"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "confirm": [1, 2],
}
DEFAULT_PARAMS = {"confirm": 1}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hc = (o + h + lo + c) / 4
    m = len(c)
    ho = np.full(m, np.nan)
    for i in range(m):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 or np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    green = pd.Series(hc > ho, index=bars_df.index)
    n = int(p["confirm"])
    held_g = green.astype(float).rolling(n).min().fillna(0).astype(bool)
    held_r = (~green).astype(float).rolling(n).min().fillna(0).astype(bool)
    long_e = (held_g & ~green.shift(n, fill_value=True)).astype(bool)
    short_e = (held_r & green.shift(n, fill_value=False)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
