"""EMA 9 / 21 crossings with both EMAs on one side of the EMA 200, broker days: the cross up above goes long, the cross down below goes short; any opposite crossing closes; reversing.
Port of FMZ strategy #476260 "Multi EMA Dynamic Trend Capture Quantitative Trading Strategy" (EMA Cross with both MinhTuan).

FMZ source id: 476260

Source
    https://www.fmz.com/strategy/476260 (PineScript v6, FMZ last modified 2024-12-27 14:59:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-150), EMA 9 / 21 / 200; trade mode Both; 10 % of equity
    crossover(ema9, ema21) and both > ema200 -> entry EMA_Cross_Long;  crossunder and both < ema200 -> entry EMA_Cross_Short;  crossunder -> close Long;  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position; a close written after a reversing entry on the same bar
      leaves the reversal standing (as #441963). The default trade mode "Both" is ported. REVERSAL
      INTENDED. The 10 % of equity size is sizing. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with an EMA 200 filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_476260_ema9_21_cross_ema200_side_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "filter": [200, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "filter": 200}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    flt = c.ewm(span=int(p["filter"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    le = up & (f > flt) & (s > flt)
    se = dn & (f < flt) & (s < flt)
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
