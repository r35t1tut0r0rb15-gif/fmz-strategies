"""UT Bot ATR trailing-line crossings, daily bars: the close crossing over the 9 x ATR 3 trailing line goes long, crossing under it goes short; reversing.
Port of FMZ strategy #474865 "动态趋势跟踪ATR多周期交易策略-Dynamic-Trend-Following-ATR-Multi-Period-Trading-Strategy" (ADET GİRMELİ Trend İz Süren Stop Strategy).

FMZ source id: 474865

Source
    https://www.fmz.com/strategy/474865 (PineScript v5, FMZ last modified 2024-12-12 16:00:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 116-365), key value 9; ATR 3; Heikin-Ashi source off; quantities 1
    trail := close > trail[1] and close[1] > trail[1] ? max(trail[1], close - 9 atr) : close < trail[1] and close[1] < trail[1] ? min(trail[1], close + 9 atr) : close > trail[1] ? close - 9 atr : close + 9 atr;  crossover(close, trail) -> entry Buy Order / Long, close Short;  crossover(trail, close) -> close Buy Order, entry Short, close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing line is the UT Bot recursion from an nz seed of 0 (a loop). The two long ids ("Buy
      Order" from the script's quantity counter and "Long") can hold only one position (pyramiding 1),
      and the buy and sell signals alternate, so the orders reduce to a reversal on each crossing; the
      closes only repeat it. The commented scanner block feeds nothing. REVERSAL INTENDED. The fixed
      quantities are not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing-line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed quantities stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG474865 (2 members, best partner #474872, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474865_ut_bot_atr3_key9_trail_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [9, 3],
    "atr_period": [3, 10],
}
DEFAULT_PARAMS = {"key": 9, "atr_period": 3}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nl = (float(p["key"]) * _atr(bars_df, p["atr_period"])).to_numpy(dtype=float)
    s = c.to_numpy(dtype=float)
    m = len(s)
    tr = np.full(m, np.nan)
    prev = 0.0                                   # nz(trail[1], 0)
    for i in range(m):
        s1 = s[i - 1] if i >= 1 else np.nan
        if s[i] > prev and s1 > prev:
            v = np.nan if np.isnan(nl[i]) else max(prev, s[i] - nl[i])
        elif s[i] < prev and s1 < prev:
            v = np.nan if np.isnan(nl[i]) else min(prev, s[i] + nl[i])
        elif s[i] > prev:
            v = s[i] - nl[i]
        else:
            v = s[i] + nl[i]
        tr[i] = v
        prev = 0.0 if np.isnan(v) else v
    t = pd.Series(tr, index=bars_df.index)
    le = (c > t) & (c.shift(1) <= t.shift(1))
    se = (t > c) & (t.shift(1) <= c.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
