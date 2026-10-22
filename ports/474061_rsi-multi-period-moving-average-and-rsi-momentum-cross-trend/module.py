"""SMA 9 / 21 crossings at RSI extremes or engulfing candles, daily bars: a cross up with RSI under 30, or a bullish engulfing candle, goes long; a cross down with RSI over 70, or a bearish engulfing candle, goes short (the short wins a bar with both); reversing.
Port of FMZ strategy #474061 "多周期均线与RSI动量交叉趋势跟踪策略-Multi-Period-Moving-Average-and-RSI-Momentum-Cross-Trend-Following-Strategy" (Comprehensive Trading Strategy).

FMZ source id: 474061

Source
    https://www.fmz.com/strategy/474061 (PineScript v5, FMZ last modified 2024-12-05 16:43:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-141), SMA 9 / 21; RSI 14, 70 / 30; engulfing patterns; 10 % of equity
    crossover(fast, slow) and rsi < 30 or bullishEngulfing -> entry Buy;  crossunder(fast, slow) and rsi > 70 or bearishEngulfing -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * "and" binds before "or", as Pine. Both entries can be sent on one bar (a cross up with RSI under
      30 on a bearish engulfing bar); the later call, the short, wins (#437773). There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. The equity share is not ported. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings at RSI extremes or engulfing candles.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_474061_sma9_21_cross_rsi_extreme_or_engulfing_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21}


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
    o, c = bars_df["open"], bars_df["close"]
    a, b = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    r = _rsi(c, 14)
    o1, c1 = o.shift(1), c.shift(1)
    bull = (c > o) & (c1 < o1) & (o < c1) & (c > o1)
    bear = (c < o) & (c1 > o1) & (o > c1) & (c < o1)
    buy = ((a > b) & (a.shift(1) <= b.shift(1)) & (r < 30)) | bull
    sell = ((a < b) & (a.shift(1) >= b.shift(1)) & (r > 70)) | bear
    false = pd.Series(False, index=bars_df.index)
    return buy & ~sell, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
