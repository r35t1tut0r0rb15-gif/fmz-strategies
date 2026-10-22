"""Pullback reactions to a composite EMA 25, broker days: in an uptrend a low reaching 0.5 % under the EMA with the close back over it goes long, in a downtrend a high reaching 0.5 % over it with the close under it goes short; reversing.
Port of FMZ strategy #482906 "Composite Trend Moving Average Reversal Trading Strategy" (Ultrajante MA Reaction Strategy).

FMZ source id: 482906

Source
    https://www.fmz.com/strategy/482906 (PineScript v5, FMZ last modified 2025-02-27 17:23:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-157), MA type EMA (menu default); periods 20 / 30, composite "Average" -> 25; reaction 0.5 %; 10 % of equity, capital 10000
    ma = ema(close, round((20 + 30) / 2));  upReaction = close > ma and low <= ma x 0.995;  downReaction = close < ma and high >= ma x 1.005
    upReaction -> close Short, entry Long;  downReaction -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The MA-type and composite-method menus keep their defaults (EMA, Average); the composite period is
      round((A + B) / 2), Pine's half-up rounding. Each reaction closes the other side and enters:
      REVERSAL INTENDED. The 10 % of equity size and the capital are sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA pullback reactions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
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

NAME = "fmz_482906_composite_ema25_pullback_reaction_0_5pct_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period_a": [20, 10],
    "reaction_perc": [0.5, 1.0],
}
DEFAULT_PARAMS = {"period_a": 20, "reaction_perc": 0.5, "period_b": 30}


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
    n = int(np.floor((int(p["period_a"]) + int(p["period_b"])) / 2 + 0.5))
    ma = c.ewm(span=n, adjust=False).mean()
    q = float(p["reaction_perc"]) / 100
    le = (c > ma) & (lo <= ma * (1 - q))
    se = (c < ma) & (h >= ma * (1 + q))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
