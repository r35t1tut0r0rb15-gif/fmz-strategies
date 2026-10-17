"""RSI extremes at 10-bar price extremes, always in, broker days: a bar making the 10-bar low while RSI 14 is below 30
but above its own 10-bar low goes long; a bar making the 10-bar high with RSI above 70 but below its 10-bar high goes
short.
Port of FMZ strategy #488907 "动态RSI低高点背离趋势策略-Dynamic-RSI-Low-High-Point-Divergence-Trend-Strategy" (RSI Divergence Strategy - Visible Signals).

FMZ source id: 488907

Source
    https://www.fmz.com/strategy/488907 (PineScript v6, FMZ last modified 2025-03-31 17:24:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 127-157), RSI 14, lookback 10, 30 / 70
    bull = low == lowest(low, 10) and rsi > lowest(rsi, 10) and rsi < 30 -> entry long
    bear = high == highest(high, 10) and rsi < highest(rsi, 10) and rsi > 70 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The windows include the current bar, as written. No exit other than the opposite entry (REVERSAL INTENDED); the
      two signals cannot fall on one bar (RSI below 30 and above 70).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rolling extremes and an oscillator.
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

NAME = "fmz_488907_rsi_extreme_at_price_extreme"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [10, 20],
    "oversold": [30, 40],
}
DEFAULT_PARAMS = {"rsi_len": 14, "lookback": 10, "oversold": 30, "overbought": 70}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    rsi = _rsi(c, int(p["rsi_len"]))
    bull = ((lo == lo.rolling(n).min()) & (rsi > rsi.rolling(n).min()) & (rsi < p["oversold"])).astype(bool)
    bear = ((h == h.rolling(n).max()) & (rsi < rsi.rolling(n).max()) & (rsi > p["overbought"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return bull, false, bear, false.copy()


def portfolio_kwargs(**params):
    return {}
