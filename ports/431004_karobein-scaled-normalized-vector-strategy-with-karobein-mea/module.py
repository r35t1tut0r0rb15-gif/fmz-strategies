"""The day's last 34-minute return (the daily close against the close of the 34-minute bar before the last one), broker days: rising above 0.0014 % goes long, falling below -0.0014 % goes short; reversing.
Port of FMZ strategy #431004 "基于态势的Karobein均值回归策略Scaled-Normalized-Vector-Strategy-with-Karobein-Mean-Reversion" (Normalized Vector Strategy, ver.3 (sc)).

FMZ source id: 431004

Source
    https://www.fmz.com/strategy/431004 (PineScript v4, FMZ last modified 2023-11-03 16:56:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 163-235), timeframe 34 (minutes), threshold 14 / 1000000; old system (lookahead on); volume switch off; Karobein oscillator only plotted
    p = security(tf 34, close, lookahead_on) / security(tf 34, close[1], lookahead_on) - 1;  crossover(p, 14 / 1e6) -> entry L;  crossunder(p, -14 / 1e6) -> entry S

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the daily header chart, security() of the lower 34-minute timeframe returns the last 34-minute bar
      inside each day (lookahead on reaches no further than the day), so p is the daily close against the
      previous 34-minute close. The 34-minute bars are counted from the broker-day start (17:00
      America/New_York), the house day; the author notes the script repaints when refreshed (weird case).
      The volume (OBV) branch is off and the Karobein oscillator only plots, so volume does not reach the
      orders: ported as not using volume (check 8). REVERSAL INTENDED. The 1-unit orders are sizing. Daily
      bars are broker days, stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, sign of the day's last intraday return.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1-unit orders stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); 34-minute buckets from its start.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431004_last_34min_return_sign_daily_reversal"
FAMILY = "intraday_return"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tf": [34, 60],
    "thresh": [14.0, 100.0],
}
DEFAULT_PARAMS = {"tf": 34, "thresh": 14.0, "div": 1000000.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # the tf-minute buckets of each broker day, counted from its nominal 17:00 America/New_York start
    tf = int(params.get("tf", DEFAULT_PARAMS["tf"]))
    ny = df.index.tz_convert("America/New_York")
    start = (ny + pd.Timedelta(hours=7)).normalize() - pd.Timedelta(hours=7)
    bucket = ((ny - start) // pd.Timedelta(minutes=tf)).astype(int)
    bc = df["close"].groupby([lab, bucket]).last()                 # bucket closes in time order
    prev = bc.shift(1)                                             # the bucket before (maybe the previous day)
    last = bc.groupby(level=0).tail(1)
    p_day = (last / prev.loc[last.index] - 1).droplevel(1)
    bars["p_tf"] = p_day.reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    x = bars_df["p_tf"]
    up = float(p["thresh"]) / float(p["div"])
    le = (x > up) & (x.shift(1) <= up)
    se = (x < -up) & (x.shift(1) >= -up)
    false = pd.Series(False, index=x.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
