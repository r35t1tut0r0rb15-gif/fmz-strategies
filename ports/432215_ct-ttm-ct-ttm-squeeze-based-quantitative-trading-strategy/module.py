"""TTM-style momentum sign, broker days: the 20-bar linear regression of the close minus half of (the 20-bar mid-range
plus the SMA 20) above zero goes long, below zero goes short; always in.
Port of FMZ strategy #432215 "基于CT-TTM指标的量化交易策略CT-TTM-Squeeze-Based-Quantitative-Trading-Strategy" (CT TTM Squeeze).

FMZ source id: 432215

Source
    https://www.fmz.com/strategy/432215 (PineScript v2, FMZ last modified 2023-11-15 16:06:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 175-198), length 20
    e1 = (highest(high, 20) + lowest(low, 20)) / 2 + sma(close, 20);  osc = linreg(close - e1 / 2, 20, 0)
    osc > 0 -> entry long;  osc < 0 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * e1 / 2 is the average of the mid-range and the SMA, as written. The band / Keltner difference
      (diff) only colours a plot. linreg(x, n, 0) is the least-squares line through the last n values,
      read at the current bar; the windows include the current bar.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, the sign of a detrended regression.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432215_ttm_momentum_sign"
FAMILY = "volatility_squeeze"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 10, 40],
}
DEFAULT_PARAMS = {"length": 20}


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    e1 = (h.rolling(n).max() + lo.rolling(n).min()) / 2 + c.rolling(n).mean()
    osc = _linreg(c - e1 / 2, n).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if osc[i] > 0:
            pos = 1
        elif osc[i] < 0:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    se = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, false, se, false.copy()))


def portfolio_kwargs(**params):
    return {}
