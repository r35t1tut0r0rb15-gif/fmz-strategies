"""Aroon 14 crossings confirmed by the last zig-zag swing, daily bars: Aroon Up crossing over Aroon Down while the last 5-bar zig-zag point was a high goes long, the mirror (last point a low) goes short; any opposite Aroon cross closes the position; reversing.
Port of FMZ strategy #474881 "自适应趋势跟踪与反转识别策略基于ZigZag与Aroon指标的量化交易系统-Adaptive-Trend-Following-and-Reversal-Detection-Strategy-A-Quantitative-Trading-System-Based-on-ZigZag-and-Aroon-Indicators" (Zig Zag + Aroon Strategy).

FMZ source id: 474881

Source
    https://www.fmz.com/strategy/474881 (PineScript v5, FMZ last modified 2024-12-12 17:21:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-158), zig-zag depth 5; Aroon 14
    high >= highest(high, 5) and dir != 1 -> lastZig := high, lastZigHigh := high, dir := 1;  low <= lowest(low, 5) and dir != -1 -> lastZig := low, lastZigLow := low, dir := -1;  crossover(aroonUp, aroonDown) and lastZig == lastZigHigh -> entry Long;  crossover(aroonDown, aroonUp) and lastZig == lastZigLow -> entry Short;  opposite crosses -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source's Aroon formula subtracts bar_index, but both lines shift together, so their crossings
      are the standard Aroon crossings (up - down = 100 x (offset of the high - offset of the low) /
      14); a tie with an earlier bar counts as the most recent. The zig-zag state is a loop (the low
      test runs after the high test). A close coinciding with the opposite entry only repeats the
      reversal (#437773), so it is masked on entry bars. REVERSAL INTENDED. No sizing code. FREQ = "1D"
      from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Aroon crossings with a zig-zag filter.
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

NAME = "fmz_474881_aroon14_cross_zigzag5_filter_reversal"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "depth": [5, 10],
    "aroon_length": [14, 25],
}
DEFAULT_PARAMS = {"depth": 5, "aroon_length": 14}


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


def _offset(x, n, side):
    """Bars back to the window's extreme (0 = this bar; a tie counts as the most recent)."""
    def f(v):
        w = v[::-1]
        return float(np.argmax(w) if side > 0 else np.argmin(w))
    return x.rolling(n).apply(f, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    k, n = int(p["depth"]), int(p["aroon_length"])
    hz = (h >= h.rolling(k).max()).to_numpy()
    lz = (lo <= lo.rolling(k).min()).to_numpy()
    m = len(h)
    last_high = np.zeros(m, dtype=bool)
    d, top = 0, False
    for i in range(m):
        if hz[i] and d != 1:
            d, top = 1, True
        if lz[i] and d != -1:
            d, top = -1, False
        last_high[i] = top if d != 0 else False
    lastlow = np.zeros(m, dtype=bool)
    d = 0
    for i in range(m):
        if hz[i] and d != 1:
            d = 1
        if lz[i] and d != -1:
            d = -1
        lastlow[i] = d == -1
    ix = bars_df.index
    diff = _offset(lo, n, -1) - _offset(h, n, 1)       # up - down, in bars (x 100 / n)
    up = (diff > 0) & (diff.shift(1) <= 0)
    dn = (diff < 0) & (diff.shift(1) >= 0)
    le = up & pd.Series(last_high, index=ix)
    se = dn & pd.Series(lastlow, index=ix)
    return le, dn & ~se, se, up & ~le


def portfolio_kwargs(**params):
    return {}
