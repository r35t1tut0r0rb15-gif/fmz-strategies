"""Crossings of an SMA 8 of the EMA 8 over / under an SMA 21 of the EMA 21, broker days, taken only within 3 bars of a confirmed 2-bar pivot high or low: the cross up goes long, the cross down goes short; reversing.
Port of FMZ strategy #476244 "基于EMA和SMA的多重指标动态趋势跟踪策略-Multi-Indicator-Dynamic-Trend-Following-Strategy-Based-on-EMA-and-SMA" (Buy Sell Pivot Point).

FMZ source id: 476244

Source
    https://www.fmz.com/strategy/476244 (PineScript v6, FMZ last modified 2024-12-27 14:12:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-211), pivot period 2; SMA 8 of EMA 8, SMA 21 of EMA 21; fixed timeframe "D"; PP SuperTrend ATR 10 x 3 (plotted only)
    fix_* = security("D", ...) on the daily chart;  ph = pivothigh(2, 2), pl = pivotlow(2, 2);  ph or pl -> last_pivot_time := bar_index
    crossover(sma(ema8, 8), sma(ema21, 21)) and bar_index - last_pivot_time <= 3 -> entry Buy;  crossunder and the same -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" request equals the daily chart (as #437508), so every fix_ series is the chart's own. A
      pivot is confirmed 2 bars after its centre bar (strict, as Pine's pivothigh / pivotlow), and
      bar_index there is the confirming bar; before the first pivot no signal is valid. The pivot
      SuperTrend, centre line and support / resistance are plotted only and do not trade. REVERSAL
      INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed MA crossings near confirmed pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_476244_sma_of_ema_cross_near_pivot_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "prd": [2, 4],
    "window": [3, 5],
}
DEFAULT_PARAMS = {"prd": 2, "window": 3, "sma1": 8, "sma2": 21}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow on the chart bars)."""
    v = np.asarray(x, dtype=float)
    m = len(v)
    out = np.zeros(m, dtype=bool)
    for t in range(2 * span, m):
        c = v[t - span]
        rest = np.concatenate([v[t - 2 * span:t - span], v[t - span + 1:t + 1]])
        if np.isnan(c) or np.isnan(rest).any():
            continue
        out[t] = (c > rest).all() if side > 0 else (c < rest).all()
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["prd"])
    piv = _pivot(h, 1, k) | _pivot(lo, -1, k)
    m = len(c)
    idx = np.arange(m)
    last = np.maximum.accumulate(np.where(piv, idx, -1))
    near = pd.Series((last >= 0) & (idx - last <= int(p["window"])), index=c.index)
    s1 = c.ewm(span=8, adjust=False).mean().rolling(int(p["sma1"])).mean()
    s2 = c.ewm(span=21, adjust=False).mean().rolling(int(p["sma2"])).mean()
    up = (s1 > s2) & (s1.shift(1) <= s2.shift(1))
    dn = (s1 < s2) & (s1.shift(1) >= s2.shift(1))
    false = pd.Series(False, index=c.index)
    return up & near, false, dn & near, false.copy()


def portfolio_kwargs(**params):
    return {}
