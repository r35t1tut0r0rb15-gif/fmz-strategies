"""KST signal-line crosses, broker days: Pring's KST (ROC 11 / 15 / 20 / 33 smoothed 9 / 14 / 8 / 15, weights 1-4) crossing
above its SMA 9 goes long, crossing below goes short; always in after the first cross.
Port of FMZ strategy #433401 "KST指标获利策略KST-Indicator-Profit-Strategy" (KST Strategy).

FMZ source id: 433401

Source
    https://www.fmz.com/strategy/433401 (PineScript v5, FMZ last modified 2023-11-27 11:37:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 159-185), ROC 11 / 15 / 20 / 33, SMA 9 / 14 / 8 / 15, signal 9
    kst = sma(roc(close, 11), 9) + 2 sma(roc(close, 15), 14) + 3 sma(roc(close, 20), 8) + 4 sma(roc(close, 33), 15);  sig = sma(kst, 9)
    crossover(kst, sig) -> entry long;  crossunder(kst, sig) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * roc() is 100 x (close - close[n]) / close[n]. strategy.entry reverses: REVERSAL INTENDED. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rates of change in percent.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433401_kst_signal_cross"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "siglen": [9, 5],
    "roc4": [33, 50],
}
DEFAULT_PARAMS = {"roc1": 11, "roc2": 15, "roc3": 20, "roc4": 33, "sma1": 9, "sma2": 14, "sma3": 8, "sma4": 15,
                  "siglen": 9}


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
    c = bars_df["close"]

    def sroc(n, s):
        cn = c.shift(int(n))
        return (100 * (c - cn) / cn).rolling(int(s)).mean()

    kst = (sroc(p["roc1"], p["sma1"]) + 2 * sroc(p["roc2"], p["sma2"]) + 3 * sroc(p["roc3"], p["sma3"])
           + 4 * sroc(p["roc4"], p["sma4"]))
    sig = kst.rolling(int(p["siglen"])).mean()
    le = ((kst > sig) & (kst.shift(1) <= sig.shift(1))).astype(bool)
    se = ((kst < sig) & (kst.shift(1) >= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
