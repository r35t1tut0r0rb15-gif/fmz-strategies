"""Close crossings of the Ichimoku leading span B (52-bar midpoint, undisplaced), broker days: the close crossing over it goes long, crossing under goes short; reversing.
Port of FMZ strategy #442206 "Ichimoku Cloud Oscillator Trading Strategy" (一目均衡表シグナル + ボリンジャーバンド).

FMZ source id: 442206

Source
    https://www.fmz.com/strategy/442206 (PineScript v5, FMZ last modified 2024-02-20 11:12:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-184), Ichimoku 9 / 26 / 52, displacement 26 (plots only); Bollinger 20 / 2 and the 1-3 sigma lines plotted only
    buy = crossover(close, leadLine2) -> entry BuyLeadLine, close SellLeadLine;  sell = crossunder(close, leadLine2) -> close BuyLeadLine, entry SellLeadLine

Interpretation choices (Pine rules in SURVEY_README.md)
    * leadLine2 is the undisplaced 52-bar midpoint (the displacement applies to the plots only). Each close
      goes with the opposite entry, one reversal. The Bollinger lines are plotted only. REVERSAL INTENDED.
      No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close / span B crossings.
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

NAME = "fmz_442206_close_ichimoku_span_b_cross_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "span_b": [52, 26],
}
DEFAULT_PARAMS = {"span_b": 52}


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
    n = int(p["span_b"])
    l2 = (lo.rolling(n).min() + h.rolling(n).max()) / 2
    up = (c > l2) & (c.shift(1) <= l2.shift(1))
    dn = (c < l2) & (c.shift(1) >= l2.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
