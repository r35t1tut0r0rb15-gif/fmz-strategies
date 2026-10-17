"""SMA 9 / 21 crosses near a remembered demand (supply) zone with a 1 % stop / 2 % target from the entry, 1-hour
bars: a cross up with the close within 1 % above the latest demand zone goes long; a cross down within 1 % below the
latest supply zone goes short. A demand zone is the low of a green bar two bars back that is the 50-bar lowest low.
Port of FMZ strategy #482859 "基于移动平均线和供需区域的动态风险管理交易系统-Moving-Average-Based-Supply-Demand-Zone-Trading-System-with-Dynamic-Risk-Management" (MA Crossover with Demand/Supply Zones + Stop Loss/Take Profit).

FMZ source id: 482859

Source
    https://www.fmz.com/strategy/482859 (PineScript v5, FMZ last modified 2025-02-20 15:39:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 98-152), SMA 9 / 21, zone lookback 50, strength 2, SL 1 %, TP 2 %
    lowest(low, 50) == low[2] and close[2] > open[2] -> demandZone = low[2] (var); supply mirrored with highs
    long = crossover(sma9, sma21) and close <= demand x 1.01; short = crossunder and close >= supply x 0.99
    entry + exit(stop / limit from strategy.position_avg_price) on signal bars

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is issued on signal bars from strategy.position_avg_price, na while flat: the port applies the 1 % / 2 %
      bracket from the fill (the evident intent), as #489289. Decision owed: keep this, or the literal behaviour.
    * The zones are var levels kept until replaced, as written (na before the first one).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the fill (decision owed).
    2 generic: PASS, moving averages, remembered swing levels and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_482859_sma_cross_near_zone_pct_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "zone_lookback": [50, 100],
    "tp_pct": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "zone_lookback": 50, "strength": 2, "sl_pct": 1.0, "tp_pct": 2.0}


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


def _var_level(x):
    """A Pine `var` level: the last value set, kept until the next one (past values only)."""
    v = x.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n, k = int(p["zone_lookback"]), int(p["strength"])
    dz = _var_level(lo.shift(k).where((lo.rolling(n).min() == lo.shift(k)) & (c.shift(k) > o.shift(k))))
    sz = _var_level(h.shift(k).where((h.rolling(n).max() == h.shift(k)) & (c.shift(k) < o.shift(k))))
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    near_d = (dz > 0) & (c <= dz * 1.01)
    near_s = (sz > 0) & (c >= sz * 0.99)
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & near_d).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & near_s).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
