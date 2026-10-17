"""Fast EMA crosses of a 5-bar Bollinger basis with the Awesome Oscillator's slope, broker days, long only: the EMA 2 crossing
above the SMA 5 with the close above it and the AO rising goes long; the EMA 2 crossing below with the close below and the
AO falling closes the long.
Port of FMZ strategy #435155 "Bollinger Band Awesome Oscillator Breakout Trading Strategy" (BB+AO STRAT).

FMZ source id: 435155

Source
    https://www.fmz.com/strategy/435155 (PineScript v3, FMZ last modified 2023-12-12 17:47:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 135-210), BB 5 x 2 (SMA basis); EMA 2; AO 5 / 34; dates from 2018-06
    AO state = ao >= 0 ? (ao > ao[1] ? 1 : 2) : (ao > ao[1] ? -1 : -2);  break_up = crossover(ema2, sma5) and close > sma5 and |AO state| == 1 -> entry long
    break_down = crossunder(ema2, sma5) and close < sma5 and |AO state| == 2 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * |AO state| == 1 means the AO rose on the bar, == 2 that it did not (whatever its sign), as
      written. The bands are drawing only. The date window is the author's: dropped. Long only. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average crosses and an oscillator slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435155_ema2_bb_basis_ao_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [5, 20],
    "fast": [2, 3],
}
DEFAULT_PARAMS = {"bb_length": 5, "fast": 2}


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
    basis = c.rolling(int(p["bb_length"])).mean()
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    hl2 = (h + lo) / 2
    ao = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    rising = ao > ao.shift(1)
    up = (fast > basis) & (fast.shift(1) <= basis.shift(1)) & (c > basis) & rising
    dn = (fast < basis) & (fast.shift(1) >= basis.shift(1)) & (c < basis) & ~rising & ao.notna()
    le = up.astype(bool)
    lx = (dn & ~up).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
