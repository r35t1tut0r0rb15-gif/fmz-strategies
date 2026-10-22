"""EMA 9 / 21 crossings on the side of the EMA 200, daily bars: the cross up over the EMA 200 goes long, the cross down under it goes short; the EMA 14 turning down closes a long (turning up closes a short); reversing.
Port of FMZ strategy #454151 "EMA趋势过滤策略EMA-Trend-Filter-Strategy" (EvilRed Trading Indicator Trend Filter).

FMZ source id: 454151

Source
    https://www.fmz.com/strategy/454151 (PineScript v5, FMZ last modified 2024-06-14 15:51:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-141), EMA 9 / 21; trend EMA 200; 'Fukuiz' EMA 14 slope
    long and ema14 < ema14[1] -> close Long;  short and ema14 > ema14[1] -> close Short
    crossover(ema9, ema21) and close > ema200 -> entry Long;  crossunder and close < ema200 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are called before the entries: a close followed by the opposite entry on the same bar
      is one reversal, and a close followed by a same-side entry leaves the position on. The EMA 14 is
      compared with its previous value (green when rising, red otherwise). REVERSAL INTENDED. No sizing
      code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with a trend filter and a slope exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454151_ema9_21_cross_ema200_side_ema14_slope_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
    "trend_len": [200, 100],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "trend_len": 200, "slope_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    t = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    e14 = c.ewm(span=int(p["slope_len"]), adjust=False).mean()
    green = (e14 > e14.shift(1)).to_numpy()
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > t)).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < t)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if pos > 0 and not green[i]:
            cur = 0
        if pos < 0 and green[i]:
            cur = 0
        if buy[i] and cur != 1:
            cur = 1
        if sell[i] and cur != -1:
            cur = -1
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
