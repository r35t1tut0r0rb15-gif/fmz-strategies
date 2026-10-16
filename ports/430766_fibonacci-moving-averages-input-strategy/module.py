"""Fibonacci moving-average crosses, broker days: the EMA 34 of ohlc4 crossing above its EMA 144 goes long; the EMA 55
crossing below the SMA 144 goes short.
Port of FMZ strategy #430766 "Fibonacci Moving Averages Input Strategy" (Fibonacci Moving Averages Input).

FMZ source id: 430766

Source
    https://www.fmz.com/strategy/430766 (PineScript v5, FMZ last modified 2023-11-01 16:42:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 306-520), ohlc4; long EMA 34 over EMA 144; short EMA 55 under SMA 144
    crossover(ema(ohlc4, 34), ema(ohlc4, 144)) -> entry long
    crossunder(ema(ohlc4, 55), sma(ohlc4, 144)) -> entry short   ("crossunder EMA or SMA" defaults to SMA)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The twenty-odd Fibonacci / visual moving averages only plot.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
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

NAME = "fmz_430766_fib_ma_crosses"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "long_len": [34, 21],
    "cross_len": [144, 89],
}
DEFAULT_PARAMS = {"long_len": 34, "cross_len": 144, "short_len": 55}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    src = (bars_df["open"] + bars_df["high"] + bars_df["low"] + bars_df["close"]) / 4
    n = int(p["cross_len"])
    l1 = src.ewm(span=int(p["long_len"]), adjust=False).mean()
    l2 = src.ewm(span=n, adjust=False).mean()
    s1 = src.ewm(span=int(p["short_len"]), adjust=False).mean()
    s2 = src.rolling(n).mean()
    xo = ((l1 > l2) & (l1.shift(1) <= l2.shift(1))).to_numpy()
    xu = ((s1 < s2) & (s1.shift(1) >= s2.shift(1))).to_numpy()
    m = len(src)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if xo[i]:
            pos = 1
        if xu[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
