"""Gaussian-channel breakouts (Ehlers 4-pole filter of hlc3, 144 sampling period, 1.414 x filtered true range) with a
rising filter and a stochastic-RSI extreme, long only, daily (broker-day) bars: a close above the upper band while the
filter rises and the stochastic RSI %K is above 80 or below 20 goes long; the close crossing back below the upper band
closes it.
Port of FMZ strategy #483064 "基于高斯通道与随机RSI的多重指标自适应交易策略-Multi-Indicator-Adaptive-Trading-Strategy-Based-on-Gaussian-Channel-and-Stochastic-RSI" (Gaussian Channel Strategy v3.0).

FMZ source id: 483064

Source
    https://www.fmz.com/strategy/483064 (PineScript v5, FMZ last modified 2025-02-21 11:28:34).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 105-187), poles 4, period 144, multiplier 1.414, reduced lag / fast response
off, stochastic RSI 3 / 3 / 14 / 14
    beta = (1 - cos(2 pi / period)) / (1.414^(2 / poles) - 1); alpha = -beta + sqrt(beta^2 + 2 beta)
    filter = f_filt9x(alpha, hlc3, 4); filtered TR alike; hband = filter + 1.414 x filtered TR
    long = filter > filter[1] and close > hband and (k > 80 or k < 20); exit = crossunder(close, hband)

Interpretation choices (Pine rules in SURVEY_README.md)
    * f_filt9x is the n-pole recursion f = alpha^n x src + sum_k (-1)^(k+1) C(n, k) (1 - alpha)^k f[k], with nz() = 0
      for missing history (and a missing first true range), as written.
    * The stochastic RSI is ta.stoch(rsi, rsi, rsi, 14) smoothed 3. %D is unused by the rules.
    * Every bar in the condition is an entry signal (same-side ignored while held). Long only; the source has no
      shorts. No stops. Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as
      #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a recursive filter channel scaled by filtered true range and a stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import math

import numpy as np
import pandas as pd

NAME = "fmz_483064_gaussian_channel_breakout_stochrsi_long"
FAMILY = "channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [144, 100],
    "mult": [1.414, 2.0],
}
DEFAULT_PARAMS = {"poles": 4, "period": 144, "mult": 1.414, "smooth_k": 3, "rsi_len": 14, "stoch_len": 14}


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


def _filt(alpha, src, n):
    """f_filt9x: n-pole Gaussian recursion; nz() = 0 for missing source values and history."""
    x = 1 - alpha
    coef = [(-1) ** (k + 1) * math.comb(n, k) * x ** k for k in range(1, n + 1)]
    s = np.nan_to_num(np.asarray(src, dtype=float), nan=0.0)
    out = np.zeros(len(s))
    a_n = alpha ** n
    for t in range(len(s)):
        f = a_n * s[t]
        for k in range(1, n + 1):
            if t - k >= 0:
                f += coef[k - 1] * out[t - k]
        out[t] = f
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, per = int(p["poles"]), float(p["period"])
    beta = (1 - math.cos(4 * math.asin(1) / per)) / (math.pow(1.414, 2 / n) - 1)
    alpha = -beta + math.sqrt(beta * beta + 2 * beta)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    filt = pd.Series(_filt(alpha, ((h + lo + c) / 3).to_numpy(), n), index=c.index)
    ftr = pd.Series(_filt(alpha, tr.to_numpy(), n), index=c.index)
    hband = filt + ftr * p["mult"]
    rsi = _rsi(c, int(p["rsi_len"]))
    m = int(p["stoch_len"])
    lo_r, hi_r = rsi.rolling(m).min(), rsi.rolling(m).max()
    k = (100 * (rsi - lo_r) / (hi_r - lo_r)).rolling(int(p["smooth_k"])).mean()
    long_e = ((filt > filt.shift(1)) & (c > hband) & ((k > 80) | (k < 20))).astype(bool)
    long_x = ((c < hband) & (c.shift(1) >= hband.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
