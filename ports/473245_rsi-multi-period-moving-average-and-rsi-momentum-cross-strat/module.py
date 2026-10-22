"""SMA 50 / 200 crossings with an RSI filter, daily bars, long only: the cross up with the RSI under 70 buys; the cross down with the RSI over 30 sells.
Port of FMZ strategy #473245 "多周期均线与RSI动量交叉策略-Multi-Period-Moving-Average-and-RSI-Momentum-Cross-Strategy" (Chỉ báo Giao dịch Cắt SMA với RSI (SMA cross with RSI)).

FMZ source id: 473245

Source
    https://www.fmz.com/strategy/473245 (PineScript v5, FMZ last modified 2024-11-28 15:39:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 80-123), SMA 50 / 200; RSI 14, 70 / 30
    crossover(sma50, sma200) and rsi < 70 -> entry Long;  crossunder and rsi > 30 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and exit tests cannot hold on the same bar. Long only. No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with an RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473245_sma50_200_cross_rsi_filter_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_period": [50, 20],
    "long_period": [200, 100],
}
DEFAULT_PARAMS = {"short_period": 50, "long_period": 200, "rsi_period": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a, b = c.rolling(int(p["short_period"])).mean(), c.rolling(int(p["long_period"])).mean()
    r = _rsi(c, int(p["rsi_period"]))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70)
    lx = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
