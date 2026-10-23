"""Broker days, long only: an up bar (the "delta volume" of the current bar only) closing above the 78.6 % level of the 21-bar range goes long; a down bar closing under the 50 % level closes it.
Port of FMZ strategy #451491 "Delta Volume with Fibonacci Levels Trading Strategy" (Delta Volume with Fibonacci Levels Strategy).

FMZ source id: 451491

Source
    https://www.fmz.com/strategy/451491 (PineScript v5, FMZ last modified 2024-05-15 10:45:58).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 91-149), delta period 14 (arrays rebuilt every bar); Fibonacci lookback 21; entry / exit price close
    buyerVolume = array.new_float() (every bar);  array.unshift(buyVol);  deltaVolume = sum(buyer) - sum(seller)  -> this bar's signed volume only
    deltaVolume > 0 and close > lowest(low, 21) + 0.786 x range -> entry Buy;  deltaVolume < 0 and close < lowest + 0.5 x range -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The arrays are created anew on every bar (no var), so the 14-bar sums hold one value: the delta
      is this bar's volume signed by its colour, and only its sign is used (weird case: volume only as
      volume > 0). The "fib618" / "fib382" levels are the 78.6 % and 50 % levels, as written. The date
      inputs feed nothing. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour against range retracement levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) only as the sign of this bar's delta (an up or down bar with volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451491_candle_colour_range_786_50_levels_long_only"
FAMILY = "level_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fib_length": [21, 50],
    "entry_level": [0.786, 0.618],
}
DEFAULT_PARAMS = {"fib_length": 21, "entry_level": 0.786, "exit_level": 0.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    delta = np.where(c > o, v, 0.0) - np.where(c < o, v, 0.0)
    n = int(p["fib_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    lvl_in = ll + (hh - ll) * float(p["entry_level"])
    lvl_out = ll + (hh - ll) * float(p["exit_level"])
    buy = (delta > 0) & (c > lvl_in).to_numpy()
    sell = (delta < 0) & (c < lvl_out).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
