"""SMA 5 / 12 crossings, broker days, long only: the cross up buys, the cross down closes. The bracket (5 % / 10 % from the entry price, moved to 2.5 % / 20 % from the latest close while in profit) is re-sent every bar and is not ported (pending).
Port of FMZ strategy #476263 "Dynamic Moving Average Crossover Trend Following Strategy with Adaptive Risk Management" (My Moving Average Crossover Strategy with Take Profit and Stop Loss).

FMZ source id: 476263

Source
    https://www.fmz.com/strategy/476263 (PineScript v6, FMZ last modified 2024-12-27 15:08:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-193), SMA 5 / 12; TP 10 / SL 5 (% of avg); dynamic TP 20 / SL 2.5 (% of the close); 100 % of equity
    crossover(sma5, sma12) -> entry Buy;  crossunder -> close Buy;  every bar: tp = avg x 1.10, sl = avg x 0.95; in a long with close > avg: tp = close x 1.20, sl = close x 0.975;  exit(Buy, limit = tp, stop = sl)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar, and while the close is above the entry price its levels are
      taken from that bar's close, so they move (and may retreat) after entry: stops() cannot express a
      level re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). Long only. The 100 % of equity size is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar bracket described (pending).
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported; the bracket inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_476263_sma5_12_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [5, 10],
    "slow": [12, 30],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 12}


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
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1))
    lx = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
