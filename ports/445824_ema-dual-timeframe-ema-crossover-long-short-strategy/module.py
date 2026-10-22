"""EMA 5 / 20 order on the day's last 2-hour bar with the day's last 3-minute EMA 5 / 20 values crossing from one day to the next, daily bars: 2-hour EMA 5 above EMA 20 with the sampled 3-minute EMAs
crossing up goes long, the mirror goes short; reversing.
Port of FMZ strategy #445824 "基于双时间框架EMA交叉信号的多空策略Dual-Timeframe-EMA-Crossover-Long-Short-Strategy" (EMA Crossover Multi-Timeframe Strategy (EMA Cross MTF)).

FMZ source id: 445824

Source
    https://www.fmz.com/strategy/445824 (PineScript v5, FMZ last modified 2024-03-22 15:01:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-180), time frames 120 and 3; EMA 5 / 20
    long = security("120", ema5) > security("120", ema20) and crossover(security("3", ema5), security("3", ema20));  short mirrored -> entry Long / entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both requests are lower time frames than the daily chart: each returns its LAST bar inside the
      daily bar (as #436765), so the 2-hour order is the day's last 2-hour bar and the 3-minute
      "crossover" compares today's last 3-minute values with yesterday's. The 2-hour bars are counted
      from the broker day's start (17:00 America/New_York), twelve per day; the 3-minute bars are
      left-labelled from the minutes, gaps kept, grouped by broker day. The commented exits are not
      ported. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest
      header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 2-hour and 3-minute values end with the daily bar.
    2 generic: PASS, EMA order with sampled lower-time-frame crossings.
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

NAME = "fmz_445824_2h_ema_order_3m_sampled_cross_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ema": [5, 9],
    "long_ema": [20, 50],
}
DEFAULT_PARAMS = {"short_ema": 5, "long_ema": 20, "tf_minutes": 120}


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
    ns, nl = int(p["short_ema"]), int(p["long_ema"])
    # 2-hour bars counted from each broker day's start (17:00 America/New_York)
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    blk = (ny - ny.normalize()) // pd.Timedelta(minutes=int(p["tf_minutes"]))
    c2 = df["close"].groupby([lab, np.asarray(blk)]).last()
    d2 = (c2.ewm(span=ns, adjust=False).mean() > c2.ewm(span=nl, adjust=False).mean()).astype(float)
    u2 = (c2.ewm(span=ns, adjust=False).mean() < c2.ewm(span=nl, adjust=False).mean()).astype(float)
    day2 = d2.index.get_level_values(0)
    keep = ~day2.duplicated(keep="last")                             # the day's last 2-hour bar
    bars["h2_up"] = pd.Series(d2.to_numpy()[keep], index=day2[keep])
    bars["h2_dn"] = pd.Series(u2.to_numpy()[keep], index=day2[keep])
    m3 = df.resample("3min", label="left", closed="left").agg({"close": "last"}).dropna(how="all")
    c3 = m3["close"]
    lab3 = broker_day(m3.index)
    bars["m3_s"] = c3.ewm(span=ns, adjust=False).mean().groupby(lab3).last()   # the day's last 3-minute bar
    bars["m3_l"] = c3.ewm(span=nl, adjust=False).mean().groupby(lab3).last()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    s, lg = bars_df["m3_s"], bars_df["m3_l"]
    up = bars_df["h2_up"] == 1.0
    dn = bars_df["h2_dn"] == 1.0
    xo = (s > lg) & (s.shift(1) <= lg.shift(1))
    xu = (s < lg) & (s.shift(1) >= lg.shift(1))
    le = up & xo
    se = dn & xu
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
