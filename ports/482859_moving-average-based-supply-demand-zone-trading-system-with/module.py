"""SMA 9 / 21 crossings near a demand / supply zone (the 50-bar extreme two bars back on a green / red bar), hourly bars: the up-cross within 1 % over the demand zone goes long, the down-cross within 1 % under the supply zone goes short, each with a 1 % stop and a 2 % target from the fill; reversing.
Port of FMZ strategy #482859 "Moving Average Based Supply Demand Zone Trading System with Dynamic Risk Management" (MA Crossover with Demand/Supply Zones + Stop Loss/Take Profit).

FMZ source id: 482859

Source
    https://www.fmz.com/strategy/482859 (PineScript v5, FMZ last modified 2025-02-20 15:39:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-152), SMA 9 / 21; zone lookback 50, strength 2; stop 1 %; target 2 %
    lowest(low, 50) == low[2] and close[2] > open[2] -> demandZone := low[2];  highest(high, 50) == high[2] and close[2] < open[2] -> supplyZone := high[2]
    crossover(sma9, sma21) and close <= demand x 1.01 -> entry Buy + exit(stop = avg x 0.99, limit = avg x 1.02);  crossunder and close >= supply x 0.99 -> entry Sell + exit(stop = avg x 1.01, limit = avg x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zones keep their last value (var) until a new one is found. The exit is sent on the signal bar,
      where position_avg_price is na from flat (or the other side's price in a reversal); it is ported as
      the 1 % / 2 % bracket around the fill, active from the fill bar (as #440797). An entry on the other
      side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The zone lines are
      drawing only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, SMA crossings near swing-extreme zones.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482859_sma9_21_cross_near_demand_supply_zone_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "zone_lookback": [50, 100],
    "take_profit_perc": [2.0, 4.0],
}
DEFAULT_PARAMS = {"zone_lookback": 50, "take_profit_perc": 2.0, "short_length": 9, "long_length": 21,
                  "zone_strength": 2, "stop_loss_perc": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _carry(v):
    """Keep the last non-na value (a Pine var level), written as a loop."""
    out = np.full(len(v), np.nan)
    last = np.nan
    for i in range(len(v)):
        if not np.isnan(v[i]):
            last = v[i]
        out[i] = last
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["short_length"])).mean()
    s = c.rolling(int(p["long_length"])).mean()
    n, k = int(p["zone_lookback"]), int(p["zone_strength"])
    d_new = lo.shift(k).where((lo.rolling(n).min() == lo.shift(k)) & (c.shift(k) > o.shift(k)))
    s_new = h.shift(k).where((h.rolling(n).max() == h.shift(k)) & (c.shift(k) < o.shift(k)))
    dz = pd.Series(_carry(d_new.to_numpy(dtype=float)), index=c.index)
    sz = pd.Series(_carry(s_new.to_numpy(dtype=float)), index=c.index)
    near_d = (dz > 0) & (c <= dz * 1.01)
    near_s = (sz > 0) & (c >= sz * 0.99)
    le = (f > s) & (f.shift(1) <= s.shift(1)) & near_d
    se = (f < s) & (f.shift(1) >= s.shift(1)) & near_s
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss_perc"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["take_profit_perc"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
