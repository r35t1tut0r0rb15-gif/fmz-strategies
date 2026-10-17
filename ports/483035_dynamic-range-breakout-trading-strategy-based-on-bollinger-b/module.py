"""Close crossing back above the lower Bollinger band with RSI 14 below 45, closed on a cross back below the upper band
with RSI above 70, long only, daily (broker-day) bars.
Port of FMZ strategy #483035 "基于布林带和相对强弱指数的动态区间突破交易策略-Dynamic-Range-Breakout-Trading-Strategy-Based-on-Bollinger-Bands-and-RSI" (Bollinger Bands + RSI Strategy).

FMZ source id: 483035

Source
    https://www.fmz.com/strategy/483035 (PineScript v5, FMZ last modified 2025-02-27 17:17:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-139), BB 20 x 2, RSI 14 (70 / 30)
    buy = crossover(close, lower) and rsi < 1.5 x 30 -> entry long; sell = crossunder(close, upper) and rsi > 70 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stdev is the population standard deviation. Long only; the source has no shorts. No stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483035_bollinger_rsi_reentry_long_1d"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [2.0, 2.5],
    "rsi_ob": [70, 60],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((c > lower) & (c.shift(1) <= lower.shift(1)) & (rsi < 1.5 * p["rsi_os"])).astype(bool)
    long_x = ((c < upper) & (c.shift(1) >= upper.shift(1)) & (rsi > p["rsi_ob"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
