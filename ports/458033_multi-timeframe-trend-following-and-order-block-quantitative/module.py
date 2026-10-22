"""SMA 14 crossings against a 14-bar 'order block' with a 1-hour EMA 50 / 200 trend, 3-hour bars: the close crossing over its SMA 14 while under the 14-bar range midpoint (so over the 14-bar low), with the 1-hour EMA 50 over the EMA 200, goes long; the mirror goes short; a 0.0896 % target and 0.0448 % stop from the fill; reversing.
Port of FMZ strategy #458033 "Multi Timeframe Trend Following and Order Block Quantitative Trading Strategy" (S&P 500 (order block with 1-hour EMA trend)).

FMZ source id: 458033

Source
    https://www.fmz.com/strategy/458033 (PineScript v5, FMZ last modified 2024-07-29 13:57:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-202), length 14; 1-hour EMA 50 / 200 (security '60'); target 0.08955 %, stop 0.04477 % of the average price
    ob = close > mid14 ? highest14 : lowest14;  crossover(close, sma14) and close > ob and ema50_1h > ema200_1h -> entry Compra;  the mirror -> entry Venta
    in a position: exit(limit = avg x (1 +- 0.0008955), stop = avg x (1 -+ 0.0004477))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The order block is the 14-bar high when the close is over the range midpoint (which the close can
      never exceed) and the 14-bar low otherwise, so a long needs a close under the midpoint and a
      short one over it, as written. The '60' request is a LOWER time frame than the 3-hour chart, so it
      returns the EMAs of the chart bar's last 1-hour bar (as #436765), built from the minutes. The
      percent inputs are divided by 100 again: 0.0008955 / 0.0004477 of the fill, active from the fill
      bar (#440797). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour
      bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header (UTC-aligned
      3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the 1-hour EMAs end with the chart bar; the bracket as fixed fractions.
    2 generic: PASS, SMA crossings against a range block with an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458033_sma14_cross_order_block_1h_ema_trend_reversal"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 28],
    "tp_frac": [0.0008955, 0.01],
    "sl_frac": [0.0004477, 0.005],
}
DEFAULT_PARAMS = {"length": 14, "tp_frac": 0.0008955, "sl_frac": 0.0004477, "ema_fast": 50, "ema_slow": 200}


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    agg = {"open": "first", "high": "max", "low": "min", "close": "last"}
    bars = df.resample(FREQ, label="left", closed="left").agg(agg).dropna(how="all")
    h1 = df.resample("1h", label="left", closed="left").agg(agg).dropna(how="all")
    ef = h1["close"].ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = h1["close"].ewm(span=int(p["ema_slow"]), adjust=False).mean()
    key = h1.index.floor(FREQ)
    bars["ema_f_1h"] = ef.groupby(key).last()          # the chart bar's last 1-hour bar
    bars["ema_s_1h"] = es.groupby(key).last()
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    ob = hh.where(c > (hh + ll) / 2, ll)
    sma = c.rolling(n).mean()
    up = (c > sma) & (c.shift(1) <= sma.shift(1))
    dn = (c < sma) & (c.shift(1) >= sma.shift(1))
    bull = bars_df["ema_f_1h"] > bars_df["ema_s_1h"]
    bear = bars_df["ema_f_1h"] < bars_df["ema_s_1h"]
    le = up & (c > ob) & bull
    se = dn & (c < ob) & bear
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
