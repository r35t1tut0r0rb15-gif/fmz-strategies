"""Trend Trader ATR line with a MACD filter, broker days: a close above the trailing line (the 21-day high less 3 x the WMA of the true range, or the low plus it) goes long when the MACD histogram is
positive; a close below it goes short; reversing.
Port of FMZ strategy #440808 "基于MACD指标的趋势交易策略-Trend-Trading-Strategy-Based-on-MACD-Indicator" (Trend Trader Strategy with MACD).

FMZ source id: 440808

Source
    https://www.fmz.com/strategy/440808 (PineScript v1, FMZ last modified 2024-02-02 11:32:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-188), length 21, multiplier 3; MACD 12 / 26 / 9 histogram filter on; dates from 2020 (window() is true)
    avgTR = wma(atr(1), 21);  hiLimit = highest(21)[1] - 3 avgTR[1];  loLimit = lowest(21)[1] + 3 avgTR[1];  ret = close above both ? hiLimit : close below both ? loLimit : ret[1]
    pos = close > ret ? 1 : close < ret ? -1 : pos[1];  pos == 1 and hist > 0 -> entry BUY;  pos == -1 -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * atr(1) is the true range; highest / lowest without a source are of the highs and lows. The line
      keeps its nz(0) start. The entries are levels; an entry while already in that direction does
      nothing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing line and MACD histogram.
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

NAME = "fmz_440808_trend_trader_line_macd_filter"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 50],
    "multiplier": [3, 2],
}
DEFAULT_PARAMS = {"length": 21, "multiplier": 3, "macd_control": True}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, k = int(p["length"]), float(p["multiplier"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    avg = _wma(tr, n)
    hi = h.rolling(n).max().shift(1) - avg.shift(1) * k
    lo_l = lo.rolling(n).min().shift(1) + avg.shift(1) * k
    hv, lv, cv = hi.to_numpy(), lo_l.to_numpy(), c.to_numpy(dtype=float)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    hist = (macd - macd.ewm(span=9, adjust=False).mean()).to_numpy()
    m = len(cv)
    pos_a = np.zeros(m, dtype=np.int8)
    ret, pos = 0.0, 0
    for i in range(m):
        if cv[i] > hv[i] and cv[i] > lv[i]:
            ret = hv[i]
        elif cv[i] < lv[i] and cv[i] < hv[i]:
            ret = lv[i]
        if cv[i] > ret:
            pos = 1
        elif cv[i] < ret:
            pos = -1
        pos_a[i] = pos
    mc = hist > 0 if p["macd_control"] else np.ones(m, dtype=bool)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((pos_a == 1) & mc, index=ix), false, pd.Series(pos_a == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
