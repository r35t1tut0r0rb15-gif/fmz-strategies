"""MACD signal-line crosses, broker days: the MACD (EMA 12 / 26) crossing above its SMA 9 signal goes long; crossing below goes
short (reversing). The multi-timeframe input is left on the chart resolution.
Port of FMZ strategy #435271 "MACD配信交叉策略MACD-Crossover-with-Signal-Strategy" (MACD with Signal).

FMZ source id: 435271

Source
    https://www.fmz.com/strategy/435271 (PineScript v2, FMZ last modified 2023-12-13 16:58:15).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 140-183), MACD 12 / 26 with an SMA 9 signal; resolution = the chart
    crossover(macd, signal) -> entry long;  crossunder(macd, signal) -> entry short   (macd and signal read through request.security at the chart resolution)

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Use Current Chart Resolution?" is true by default: request.security at the chart's own
      resolution returns the chart's values (no higher-timeframe read). The custom resolution (60)
      is not used. The rule macd_chk = smd and outMacD ? outMacD : na turns a MACD of exactly 0 into
      na: ignored (a float equality at zero). strategy.entry reverses: REVERSAL INTENDED. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435271 (2 members, best partner #438464, Jaccard 0.826); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435271_macd_signal_cross_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    le = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).fillna(False).astype(bool)
    se = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
