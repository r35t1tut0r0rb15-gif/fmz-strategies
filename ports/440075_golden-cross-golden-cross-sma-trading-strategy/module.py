"""SMA 13 / 30 crosses against the weekly trend, 1-hour bars: an SMA 13 cross over the SMA 30 with a slope gap, when 7 bars earlier the price was under the last completed broker week's close, goes long; the
mirror goes short; each trade has a 12 % stop and a 25 % target; reversing.
Port of FMZ strategy #440075 "双均线交叉-golden-cross-交易策略Golden-Cross-SMA-Trading-Strategy" (KISS Strategy: SMA + EMA).

FMZ source id: 440075

Source
    https://www.fmz.com/strategy/440075 (PineScript v4, FMZ last modified 2024-01-26 14:29:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 218-372), SMA 13 / 30 / 200 (200 plot only); weeks in trend 1; slope factor 0.01 (price units); SMA check on, MACD check off; stop 12 %, target 25 %
    BearTrend = wcp[1] > price (WiT 1);  BullTrend = wcp[1] < price;  StrongSlope = | |sma13 - sma13[2]| - |sma30 - sma30[2]| | > 0.01
    SMAbuy = crossover(sma13, sma30) and StrongSlope and BearTrend[7] -> entry HC-Long;  SMAsell = crossunder and StrongSlope and BullTrend[7] -> entry HC-Short;  exit(stop = avg x 0.88 / 1.12, limit = avg x 1.25 / 0.75)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security("W") without lookahead is read as the last completed higher bar: the
      previous broker week's last close (a broker week runs Monday to Friday by broker-day label), built
      from the module's own bars; [1] is the previous chart bar's value. BearTrend[WiT x 7] is 7 chart
      bars back, as written. Criterion 2: the slope gap of 0.01 price units becomes a fraction of the
      close, 2.4e-7 (the BTC reading near 42000). The bracket is a fixed 12 % / 25 % of the average
      (fill) price, re-sent at the same levels: the port starts it at the fill. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks; percent bracket from the fill.
    2 generic: ADAPT, price-unit slope gap -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week for the weekly close (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440075_kiss_sma13_30_weekly_trend_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sh_len": [13, 20],
    "lg_len": [30, 50],
}
DEFAULT_PARAMS = {"sh_len": 13, "lg_len": 30, "wit": 1, "slope_frac": 2.4e-7, "sl": 0.12, "tp": 0.25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk_close = c.groupby(week).last()
    wcp = pd.Series(wk_close.shift(1).reindex(week).to_numpy(), index=c.index)   # last completed week
    k = int(p["wit"])
    bear = (wcp.shift(k) > c) & wcp.shift(k).notna()
    bull = (wcp.shift(k) < c) & wcp.shift(k).notna()
    a = c.rolling(int(p["sh_len"])).mean()
    b = c.rolling(int(p["lg_len"])).mean()
    slope = ((a - a.shift(2)).abs() - (b - b.shift(2)).abs()).abs() / c > float(p["slope_frac"])
    back = 7 * k
    up = (a > b) & (a.shift(1) <= b.shift(1)) & slope & bear.shift(back, fill_value=False)
    dn = (a < b) & (a.shift(1) >= b.shift(1)) & slope & bull.shift(back, fill_value=False)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
