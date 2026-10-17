"""Closes above a Gaussian-weighted channel (20 bars, 2 deviations) with the stochastic RSI K above D go long,
closed by a close back under the upper band, long only, daily bars.
Port of FMZ strategy #482786 "高斯通道趋势跟踪与随机相对强弱指标交易策略-Gaussian-Channel-Trend-Following-with-Stochastic-RSI-Trading-Strategy" (Gaussian Channel + Stoch RSI Strategy).

FMZ source id: 482786

Source
    https://www.fmz.com/strategy/482786 (PineScript v5, FMZ last modified 2025-02-20 11:01:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 101-166), Gaussian 20 x 2, RSI 14, stochastic RSI 14 smoothed 3 / 3
    mid = sum(close[i] w_i) / sum(w_i), w_i = exp(-(i - 9.5)^2 / (2 (20/6)^2)), i = 0..19 (past bars only);
    std the same-weighted deviation; upper = mid + 2 std
    close > upper and k > d and not long -> entry long; close < upper and long -> close long
    only from 2018-01-01 00:00 to 2069-01-01

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel weights lags 0-19 (no future bars); na until 20 bars exist.
    * Clock rule (check 9 / C6): the date range is read as UTC; no entries or exits before 2018-01-01 00:00 UTC
      (as written; it matters only for data before 2018).
    * Entries and exits cannot fall on one bar. Long only. Signal module, no stops. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a weighted channel and a stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and the 0.1 % commission quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule; trading from 2018-01-01
00:00 UTC.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482786_gaussian_channel_break_stoch_rsi_long"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "multiplier": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "multiplier": 2.0, "rsi_len": 14, "stoch_len": 14, "k_len": 3, "d_len": 3}
START = pd.Timestamp("2018-01-01", tz="UTC")


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


def _gauss_channel(c, n):
    half = (n - 1) / 2.0
    denom = (n / 6.0) ** 2
    w = np.exp(-((np.arange(n) - half) ** 2) / (2 * denom))
    v = c.to_numpy(dtype=float)
    mid = np.convolve(v, w)[:len(v)] / w.sum()            # mid[t] = sum_i v[t - i] w[i] / sum w
    sq = np.convolve(v * v, w)[:len(v)] / w.sum()
    std = np.sqrt(np.maximum(sq - mid * mid, 0.0))
    mid[:n - 1] = np.nan
    std[:n - 1] = np.nan
    return pd.Series(mid, index=c.index), pd.Series(std, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    mid, std = _gauss_channel(c, int(p["length"]))
    upper = mid + p["multiplier"] * std
    rsi = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    rl, rh = rsi.rolling(sn).min(), rsi.rolling(sn).max()
    stoch = 100 * (rsi - rl) / np.maximum(rh - rl, 1e-10)
    k = stoch.rolling(int(p["k_len"])).mean()
    d = k.rolling(int(p["d_len"])).mean()
    live = pd.Series(bars_df.index >= START, index=bars_df.index)
    long_e = ((c > upper) & (k > d) & live).astype(bool)
    long_x = ((c < upper) & live).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
