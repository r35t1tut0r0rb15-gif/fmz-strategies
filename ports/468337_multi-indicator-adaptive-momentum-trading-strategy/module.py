"""Broker days: a positive MACD histogram (12 / 26 / 9) with the VWMA 20 above the VWMA 50 goes long, a negative histogram with the VWMA 20 below the VWMA 50 goes short; a long closes when the MACD line crosses under its signal, a short when it crosses over; reversing.
Port of FMZ strategy #468337 "Multi Indicator Adaptive Momentum Trading Strategy" (MACD & VWMA Equal Basis).

FMZ source id: 468337

Source
    https://www.fmz.com/strategy/468337 (PineScript v5, FMZ last modified 2024-09-26 16:25:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 139-194), MACD 12 / 26 / 9; VWMA 20 / 50; qty = equity x leverage / close
    longEntry = histogram > 0 and vwma20 > vwma50 -> entry Long;  longExit = crossunder(macdLine, signalLine) -> close Long
    shortEntry = histogram < 0 and vwma20 < vwma50 -> entry Short;  shortExit = crossover(macdLine, signalLine) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are states, sent on every qualifying bar; an entry while in that position adds nothing.
      A crossing-under bar has a negative histogram, so a long's close can meet a short entry on that bar:
      the entry reverses (closes act only on a position the bar's entries leave unchanged); likewise for
      the short. After a close the strategy re-enters as soon as the entry state holds again. vwma(x, n)
      = sma(x x volume, n) / sma(volume, n). The qty (all equity x leverage 1) is sizing; the commission
      input is computed but never used. REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram states filtered by VWMA 20 / 50 with MACD crossing exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x leverage / close stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) as the VWMA weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468337_macd_hist_vwma20_50_state_cross_exit_reversal"
FAMILY = "macd"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vw_fast": [20, 10],
    "vw_slow": [50, 100],
}
DEFAULT_PARAMS = {"vw_fast": 20, "vw_slow": 50}


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


def _vwma(x, v, n):
    return (x * v).rolling(n).mean() / v.rolling(n).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    hist = macd - sig
    vf, vs = _vwma(c, v, int(p["vw_fast"])), _vwma(c, v, int(p["vw_slow"]))
    le = (hist > 0) & (vf > vs)
    se = (hist < 0) & (vf < vs)
    lx = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & ~se
    sx = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & ~le
    return le.astype(bool), lx.astype(bool), se.astype(bool), sx.astype(bool)


def portfolio_kwargs(**params):
    return {}
