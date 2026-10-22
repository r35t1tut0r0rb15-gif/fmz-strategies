"""SMA 10 / 50 crossings or Bollinger 20 / 2 extremes with RSI 14, broker days: an SMA up-cross, or a close under the lower band with RSI under 30, goes long; an SMA down-cross, or a close over the upper band with RSI over 70, closes the long and goes short; reversing.
Port of FMZ strategy #485293 "Multi Strategy Adaptive Market Condition Trading System" (Adaptive Trading Strategy).

FMZ source id: 485293

Source
    https://www.fmz.com/strategy/485293 (PineScript v5, FMZ last modified 2025-03-07 09:59:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 156-206), SMA 10 / 50; RSI 14 / 30 / 70; Bollinger 20 x 2
    buy = (sma10 > sma50 and crossover(sma10, sma50)) or (close < lower and rsi < 30) -> entry Buy
    sell = (sma10 < sma50 and crossunder(sma10, sma50)) or (close > upper and rsi > 70) -> close Buy, entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "strong buy" pattern is a label only. A short is closed only by a buy, which reverses it; each
      sell closes the long and enters short: REVERSAL INTENDED. No sizing code. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings or band / RSI extremes.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_485293_sma10_50_cross_or_bb_rsi_extreme_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 50}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    r = _rsi(c, 14)
    basis, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    up, dn = basis + 2 * sd, basis - 2 * sd
    le = ((f > s) & (f.shift(1) <= s.shift(1))) | ((c < dn) & (r < 30))
    se = ((f < s) & (f.shift(1) >= s.shift(1))) | ((c > up) & (r > 70))
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
