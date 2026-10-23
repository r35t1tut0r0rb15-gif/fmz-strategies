"""A volume-weighted MACD (EMA 25 against EMA 29 of volume x close over EMA of volume, signal EMA 9): the line crossing over its signal goes long, crossing under goes short; broker days, reversing.
Port of FMZ strategy #434436 "Weighted Quantitative Moving Average Crossover Trading Strategy" (Brad VWMACD Strategy 2233).

FMZ source id: 434436

Source
    https://www.fmz.com/strategy/434436 (PineScript v3, FMZ last modified 2023-12-06 12:05:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 129-184), fast 25, slow 29, signal 9; window 2018-09 ..
    xVMACD = ema(v c, 25) / ema(v, 25) - ema(v c, 29) / ema(v, 29);  signal = ema(xVMACD, 9)
    crossover(xVMACD, signal) -> entry L, close S;  crossunder -> entry S, close L

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "x Long_period / x Long_period" factors cancel. The closes come after the entries and act on
      the side the opposite entry already reverses. The window from 2018-09 is dropped. REVERSAL INTENDED.
      100 % of equity and the commission are sizing and costs. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-weighted MACD crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, commission 0.18 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume-weighted MACD; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); the author's 2018-09 start dropped.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434436_vwmacd_25_29_signal_cross_daily_reversal"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [25, 12],
    "slow_ma": [29, 26],
}
DEFAULT_PARAMS = {"fast_ma": 25, "slow_ma": 29, "signal": 9}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]

    def vw(n):
        ev = _ema(v, n)
        return _ema(v * c, n) / ev.where(ev != 0)

    vm = vw(int(p["fast_ma"])) - vw(int(p["slow_ma"]))
    sig = _ema(vm, int(p["signal"]))
    up = (vm > sig) & (vm.shift(1) <= sig.shift(1))
    dn = (vm < sig) & (vm.shift(1) >= sig.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
