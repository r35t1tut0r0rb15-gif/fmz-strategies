"""EMA 10 / 21 crossings of the day's last 4-hour values, daily bars: the 4-hour EMA 10 crossing over the EMA 21 (as read at the end of each day) goes long, under goes short; reversing.
Port of FMZ strategy #443104 "双EMA金叉死叉趋势追踪策略Dual-EMA-Crossover-Trend-Tracking-Strategy" (Ema cross strat).

FMZ source id: 443104

Source
    https://www.fmz.com/strategy/443104 (PineScript v3, FMZ last modified 2024-02-29 11:45:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-223), EMA 21 / 10 on 240 minutes (lookahead off); margin on; dates (testPeriod true)
    ema2 = security(240, ema(close, 21));  ema3 = security(240, ema(close, 10));  mylong = crossover(ema3, ema2);  myshort = crossunder(ema3, ema2)
    in_long / in_short from the latest crossing time;  crossover(in_long, 1.9) and position <= 0 -> entry Long;  crossover(in_short, 1.9) and position >= 0 -> entry Short (Margin on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 240-minute request from a daily chart is a lower time frame: its value is the day's last
      4-hour bar (as #436765), with the 4-hour bars counted from the broker day's start (six per day),
      built from minutes in precompute. The in_long / in_short flags turn 2 exactly on alternating
      crossings, so the entries are the crossings themselves; with Margin on the long close is skipped
      and the short entry reverses. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 4-hour values end with the day.
    2 generic: PASS, lower-time-frame EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443104_last_4h_ema10_21_cross_daily_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len3": [10, 5],
    "len2": [21, 50],
}
DEFAULT_PARAMS = {"len3": 10, "len2": 21}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    # 4-hour bars counted from each broker day's start (17:00 America/New_York): six per day
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    blk = np.asarray((ny - ny.normalize()) // pd.Timedelta(minutes=240))
    c4 = df["close"].groupby([lab, blk]).last()
    day4 = c4.index.get_level_values(0)
    s4 = pd.Series(c4.to_numpy(), index=pd.RangeIndex(len(c4)))
    for col, n in (("ema_s", int(p["len3"])), ("ema_l", int(p["len2"]))):
        e = s4.ewm(span=n, adjust=False).mean().to_numpy()
        last = pd.Series(e, index=day4)
        last = last[~day4.duplicated(keep="last")]           # the day's last 4-hour bar
        bars[col] = last.reindex(bars.index).to_numpy()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    a, b = bars_df["ema_s"], bars_df["ema_l"]
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    false = pd.Series(False, index=a.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
