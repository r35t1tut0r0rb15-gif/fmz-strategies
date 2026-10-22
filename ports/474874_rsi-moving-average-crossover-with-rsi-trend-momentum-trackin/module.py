"""SMA 9 / 21 crossings with an RSI 50 filter, daily bars: the cross up with RSI over 50 goes long, the cross down under 50 goes short; reversing. The 1 % / 2 % bracket re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #474874 "均线交叉结合RSI趋势动量跟踪策略-Moving-Average-Crossover-with-RSI-Trend-Momentum-Tracking-Strategy" (MA RSI Strategy).

FMZ source id: 474874

Source
    https://www.fmz.com/strategy/474874 (PineScript v5, FMZ last modified 2024-12-12 16:22:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-141), SMA 9 / 21; RSI 14, 50; stop 1 %, target 2 % of the current close (every bar)
    crossover(sma9, sma21) and rsi > 50 -> entry Long;  crossunder and rsi < 50 -> entry Short;  every bar: exit(Long, stop = close x 0.99, limit = close x 1.02), exit(Short, mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-sent on every bar from that bar's close, so the levels move after entry: a level
      re-set every bar is not ported (as #438034, mark trailing_stop_pending). Positions end at the
      opposite entry until then. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with an RSI filter; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474874_sma9_21_cross_rsi50_reversal_bracket_pending"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_ma": [9, 5],
    "long_ma": [21, 50],
}
DEFAULT_PARAMS = {"short_ma": 9, "long_ma": 21}


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
    a, b = c.rolling(int(p["short_ma"])).mean(), c.rolling(int(p["long_ma"])).mean()
    r = _rsi(c, 14)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r > 50)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r < 50)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
