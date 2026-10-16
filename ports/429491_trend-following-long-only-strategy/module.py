"""Smoothed 200-bar channel-centre trend, long only, broker days: the EMA 3 of the trend flag (SMA 3 of close beyond
the centre +/- 0.5 ATR) crossing above zero goes long, crossing below zero closes the long.
Port of FMZ strategy #429491 "Trend Following Long Only Strategy" (Trend Following Long Only Strategy).

FMZ source id: 429491

Source
    https://www.fmz.com/strategy/429491 (PineScript v4, FMZ last modified 2023-10-17 15:55:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 121-145), lookback 200, smoother 5, ATR 10 x 0.5
    center = (ema(highest(high,200),5) + ema(lowest(low,200),5)) / 2; upper / lower = center +/- 0.5 atr(10)
    trend = ema(sma(close,3) > upper ? 1 : sma(close,3) < lower ? -1 : 0, 3)
    crossover(trend, 0) -> entry long; crossunder(trend, 0) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest / lowest include the current bar; ATR is Wilder's.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an ATR multiple around a price channel.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429491_channel_center_trend_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [200, 100],
    "atr_mult": [0.5, 1.0],
}
DEFAULT_PARAMS = {"lookback": 200, "smoother": 5, "atr_length": 10, "atr_mult": 0.5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    vola = _rma(tr, int(p["atr_length"])) * p["atr_mult"]
    n, sm = int(p["lookback"]), int(p["smoother"])
    lband = lo.rolling(n).min().ewm(span=sm, adjust=False).mean()
    hband = h.rolling(n).max().ewm(span=sm, adjust=False).mean()
    center = (hband + lband) / 2
    price = c.rolling(3).mean()
    raw = pd.Series(np.where(price > center + vola, 1.0, np.where(price < center - vola, -1.0, 0.0)), index=c.index)
    trend = raw.ewm(span=3, adjust=False).mean()
    long_e = ((trend > 0) & (trend.shift(1) <= 0)).astype(bool)
    long_x = ((trend < 0) & (trend.shift(1) >= 0)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
