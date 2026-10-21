"""Heikin-Ashi closes of intraday bars on a daily chart, broker days: the EMA 16 of the day's last 300-minute Heikin-Ashi close crossing over the EMA 21 of the day's last 15-minute Heikin-Ashi close goes long,
crossing under goes short; reversing.
Port of FMZ strategy #437400 "动量均线交叉和MACD过滤的海肯阿什蜡烛策略Momentum-Crossover-Moving-Average-and-MACD-Filter-Heikin-Ashi-Candlestick-Strategy" (HAS V2).

FMZ source id: 437400

Source
    https://www.fmz.com/strategy/437400 (PineScript v2, FMZ last modified 2024-01-02 12:18:03).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 212-252), HA time frames 15 and 300 (minutes) on a daily chart, shifts 0, EMA 16 / 21; MACD filter off
    ha_close = security(heikinashi, "15", close);  mha_close = security(heikinashi, "300", close);  fma = ema(mha_close, 16);  sma = ema(ha_close, 21)
    golong = crossover(fma, sma) (MACD filter off) -> entry Long;  goshort = crossunder -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A Heikin-Ashi close is the bar's own ohlc4. The intraday requests from a daily chart are read as the
      day's LAST 15-minute and 300-minute bars (a lower time frame returns its last bar inside the chart
      bar, as #436765), counted from the broker day's start (17:00 America/New_York); the last 300-minute
      bucket of a day is shorter (1440 is not a multiple of 300). The MACD filter is off by default and not
      ported. REVERSAL INTENDED. No sizing code. Daily bars are broker days, stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; intraday values end with the daily bar.
    2 generic: PASS, average crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430040 (2 members, best partner #430040, Jaccard 0.747); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone), intraday buckets counted from its start; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437400_intraday_ha_close_ema_cross"
FAMILY = "ma_cross"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fama": [16, 10],
    "sloma": [21, 30],
}
DEFAULT_PARAMS = {"fama": 16, "sloma": 21, "res_minutes": 15, "res1_minutes": 300}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _last_bucket_ohlc4(df, lab, mos, minutes):
    key = np.asarray(mos // pd.Timedelta(minutes=minutes))
    b = df.groupby([lab, key]).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    v = (b["open"] + b["high"] + b["low"] + b["close"]) / 4
    day = v.index.get_level_values(0)
    v = v[~day.duplicated(keep="last")]                   # the day's last bucket
    v.index = v.index.get_level_values(0)
    return v


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    mos = ny - ny.normalize()                              # time since the broker day's start
    bars["ha_res"] = _last_bucket_ohlc4(df, lab, mos, int(p["res_minutes"]))
    bars["ha_res1"] = _last_bucket_ohlc4(df, lab, mos, int(p["res1_minutes"]))
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    fma = bars_df["ha_res1"].ewm(span=int(p["fama"]), adjust=False).mean()
    sma = bars_df["ha_res"].ewm(span=int(p["sloma"]), adjust=False).mean()
    up = (fma > sma) & (fma.shift(1) <= sma.shift(1))
    dn = (fma < sma) & (fma.shift(1) >= sma.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
