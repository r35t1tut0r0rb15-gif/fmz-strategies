"""A new 10-bar low with RSI 14 above its 10-bar low and under 30 goes long; a new 10-bar high with RSI under its 10-bar high and over 70 goes short; broker days, reversing.
Port of FMZ strategy #488907 "动态RSI低高点背离趋势策略-Dynamic-RSI-Low-High-Point-Divergence-Trend-Strategy" (RSI Divergence Strategy - Visible Signals).

FMZ source id: 488907

Source
    https://www.fmz.com/strategy/488907 (PineScript v6, FMZ last modified 2025-03-31 17:24:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-170), RSI 14; lookback 10; 30 / 70
    low == lowest(low, 10) and rsi > lowest(rsi, 10) and rsi < 30 -> entry Long;  high == highest(high, 10) and rsi < highest(rsi, 10) and rsi > 70 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 10-bar windows include the signal bar, as written. No exits: the opposite entry reverses
      (REVERSAL INTENDED). No sizing code. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price / RSI divergence at extremes.
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

NAME = "fmz_488907_rsi14_divergence_10bar_extreme_reversal"
FAMILY = "rsi_divergence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [10, 20],
    "oversold": [30, 40],
}
DEFAULT_PARAMS = {"lookback": 10, "oversold": 30, "rsiLength": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["lookback"])
    r = _rsi(c, int(p["rsiLength"]))
    os_ = float(p["oversold"])
    le = (lo == lo.rolling(k).min()) & (r > r.rolling(k).min()) & (r < os_)
    se = (h == h.rolling(k).max()) & (r < r.rolling(k).max()) & (r > 100 - os_)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
