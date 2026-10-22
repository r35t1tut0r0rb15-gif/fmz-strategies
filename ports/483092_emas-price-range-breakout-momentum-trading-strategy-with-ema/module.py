"""Closes beyond the previous broker day's high / low with the EMA 9 / 21 side, hourly bars: over the high with EMA 9 over EMA 21 goes long, under the low with it under goes short, each with a 30-tick stop and a 60-tick target from the fill read as 0.15 % / 0.30 %; reversing.
Port of FMZ strategy #483092 "基于日内价格区间突破的动量交易策略结合EMAs指标优化-Price-Range-Breakout-Momentum-Trading-Strategy-with-EMAs-Optimization" (GER40 Momentum Breakout Scalping).

FMZ source id: 483092

Source
    https://www.fmz.com/strategy/483092 (PineScript v5, FMZ last modified 2025-02-21 13:20:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-154), stop 30 ticks; RR 2; time filter off; security("D", high[1] / low[1]); EMA 9 / 21; 1 % of equity, capital 10000
    close > security("D", high[1]) and ema9 > ema21 -> entry Long + exit(stop = avg - 30 ticks, limit = avg + 60 ticks)
    close < security("D", low[1]) and ema9 < ema21 -> entry Short + exit(stop = avg + 30 ticks, limit = avg - 60 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security("D", high[1]) without lookahead is the previous completed broker day's high (as #458137),
      built in precompute from the minutes; likewise the low. The time filter is off by default.
    * Criterion 2: the bracket is 30 / 60 ticks; on the header's SOL_USDT (tick 0.01, about 200 USDT) that
      is 0.30 / 0.60, read as 0.15 % / 0.30 % of the fill (as the tick readings of #458242, at the
      header's prices). The exit sent on the flat signal bar has na levels; it is ported from the fill,
      active from the fill bar (as #440797); repeat signals re-send the same levels around the same
      average price. An entry on the other side reverses (REVERSAL INTENDED). Stop module:
      portfolio_kwargs {} (driver D4). The 1 % of equity size and the capital are sizing. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: ADAPT, tick bracket read as percents at the header's SOL prices.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity and capital stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the previous day's high / low; time filter off.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483092_prev_day_high_low_break_ema9_21_tick_bracket_reversal"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [0.0015, 0.005],
    "risk_reward": [2.0, 1.5],
}
DEFAULT_PARAMS = {"stop_frac": 0.0015, "risk_reward": 2.0, "ema_fast": 9, "ema_slow": 21}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    df = raw_1m_df[["high", "low"]].dropna(how="all")
    lab = broker_day(df.index)
    day = df.groupby(lab).agg({"high": "max", "low": "min"})
    prev = day.shift(1)                       # the previous broker day with data
    blab = broker_day(bars.index)
    bars["prev_high"] = prev["high"].reindex(blab).to_numpy()
    bars["prev_low"] = prev["low"].reindex(blab).to_numpy()
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    le = (c > bars_df["prev_high"]) & (f > s)
    se = (c < bars_df["prev_low"]) & (f < s)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    a = float(p["stop_frac"])
    sl = pd.Series(a, index=idx).shift(1)
    tp = pd.Series(a * float(p["risk_reward"]), index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
