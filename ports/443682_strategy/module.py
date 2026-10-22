"""Close against its 120-day SMA, daily bars, long only: a daily close at or above the SMA 120 goes long; a close under it closes.
Port of FMZ strategy #443682 "均线突破" (Moving average breakout (JavaScript)).

FMZ source id: 443682

Source
    https://www.fmz.com/strategy/443682 (javascript, FMZ last modified 2024-03-24 13:45:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 32-58), PERIOD 120; daily records; spot buy 95 % of the balance, sell all
    on each new daily record: ma = MA(records, 120);  lastK.Close >= ma and not bought -> Buy;  lastK.Close < ma and bought -> Sell all

Interpretation choices (rules in SURVEY_README.md)
    * The bot acts once per new daily record on the forming bar; the port evaluates the rule on
      completed broker days and the engine fills at the next open (as the house JavaScript ports). The
      95 % balance size is sizing. Long only. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS (with note), acts once per new bar on the forming bar; the port evaluates on completed bars.
    2 generic: PASS, close vs SMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the balance-fraction size stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443682_close_vs_sma120_daily_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [120, 50],
}
DEFAULT_PARAMS = {"period": 120}


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
    ma = c.rolling(int(p["period"])).mean()
    le = c >= ma
    lx = c < ma
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
