"""Broker days: a close above the last confirmed swing high (pivot 6 / 6) on volume at or above its 200-day average goes long, a close below the last swing low on such volume goes short; each trade takes profit 2 % from its fill; reversing.
Port of FMZ strategy #474676 "EMA-SMA趋势跟踪与波段交易策略结合成交量过滤和百分比止盈止损系统-EMA-SMA-Trend-Following-with-Swing-Trading-Strategy-Combined-Volume-Filter-and-Percentage-Take-Profit-Stop-Loss-System" (Swing High/Low Strategy with Volume, EMA/SMA Crossovers, Percentage TP and Trailing Stop).

FMZ source id: 474676

Source
    https://www.fmz.com/strategy/474676 (PineScript v5, FMZ last modified 2024-12-11 15:12:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 90-188), pivots 6 / 6 (fixnan); volume SMA 200; TP 2 % of position_avg_price; trail_offset = avg x 1 % (no activation)
    longCondition = close > fixnan(pivothigh(6, 6)) and volume >= sma(volume, 200) -> entry Long;  shortCondition = close < fixnan(pivotlow(6, 6)) and volume >= volMa -> entry Short
    exit("Long Exit", "Long", stop = na, trail_offset = position_avg_price x 0.01, limit = position_avg_price x 1.02) every bar (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_offset without trail_price / trail_points places no trailing stop (#441084), so the only exit
      is the 2 % limit from the fill. It is re-sent every bar from position_avg_price, so it first acts
      from the bar after the fill: ported as tp_stop 0.02 from the fill (stated approximation, as
      #429494). The swing levels are the last confirmed pivot values (6 bars after each pivot). The
      entries are states; an opposite entry reverses. The EMA / SMA and the alert flags only plot.
      REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 2 % target from the fill.
    2 generic: PASS, swing-level breakouts on high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 200; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474676_swing_pivot_breakout_volume200_2pct_target_reversal"
FAMILY = "swing_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "pivot": [6, 10],
    "tp": [0.02, 0.04],
}
DEFAULT_PARAMS = {"pivot": 6, "vol_len": 200, "tp": 0.02}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    k = int(p["pivot"])
    fh, vh = _pivot_hit(h, 1, k, k)
    fl, vl = _pivot_hit(lo, -1, k, k)
    ph = _fixnan(pd.Series(np.where(fh, vh, np.nan), index=c.index))
    pl = _fixnan(pd.Series(np.where(fl, vl, np.nan), index=c.index))
    vol_ok = v >= v.rolling(int(p["vol_len"])).mean()
    sell = (c < pl) & vol_ok
    buy = (c > ph) & vol_ok & ~sell        # later call wins on a two-sided bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
