"""Gaussian channel (4 poles, period 144, true-range band x 1.414) with Stochastic RSI 14 / 14 / 3 extremes, broker days, long only: a rising filter with the close over the upper band and %K over 80 or under 20 goes long; the close crossing back under the upper band closes.
Port of FMZ strategy #483064 "基于高斯通道与随机RSI的多重指标自适应交易策略-Multi-Indicator-Adaptive-Trading-Strategy-Based-on-Gaussian-Channel-and-Stochastic-RSI" (Gaussian Channel Strategy v3.0).

FMZ source id: 483064

Source
    https://www.fmz.com/strategy/483064 (PineScript v5, FMZ last modified 2025-02-21 11:28:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-196), poles 4; period 144; TR multiplier 1.414; reduced-lag and fast-response off; Stochastic RSI 14 / 14 / 3 / 3; 100 % of equity, capital 1000, commission 0.1 %
    beta = (1 - cos(2 pi / 144)) / (1.414^(2 / 4) - 1);  alpha = -beta + sqrt(beta^2 + 2 beta);  filter = 4-pole recursive Gaussian of hlc3;  trFilter = same of ta.tr
    long = filter > filter[1] and close > filter + 1.414 trFilter and (k > 80 or k < 20) -> entry Long;  crossunder(close, hband) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The n-pole filter is the source's f_filt9x recursion: f = a^n x src + sum over k = 1..n of
      (-1)^(k+1) C(n, k) (1 - a)^k f[k], with nz() reading 0 before the start; ta.tr is na on the first
      bar (read as 0 by nz). Reduced-lag and fast-response modes are off by default, so only the 4-pole
      main filter is used. Long only. The 100 % of equity size and the capital are sizing; the commission
      is a cost (the house cost model applies). Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Gaussian channel breakout with Stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and capital stored, not ported.
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

NAME = "fmz_483064_gaussian4_144_channel_upper_break_stochrsi_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [144, 72],
    "mult": [1.414, 2.0],
}
DEFAULT_PARAMS = {"period": 144, "mult": 1.414, "poles": 4, "smooth_k": 3, "length_rsi": 14, "length_stoch": 14}


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


def _gauss(src, a, n):
    """The source's f_filt9x for n poles: f = a^n s + sum_k (-1)^(k+1) C(n, k) (1 - a)^k f[k]; nz() as 0."""
    from math import comb
    s = np.nan_to_num(src.to_numpy(dtype=float), nan=0.0)
    x = 1 - a
    coef = [(-1) ** (k + 1) * comb(n, k) * x ** k for k in range(1, n + 1)]
    m = len(s)
    f = np.zeros(m)
    an = a ** n
    for t in range(m):
        acc = an * s[t]
        for k in range(1, n + 1):
            if t - k >= 0:
                acc += coef[k - 1] * f[t - k]
        f[t] = acc
    return pd.Series(f, index=src.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, per = int(p["poles"]), int(p["period"])
    beta = (1 - np.cos(4 * np.arcsin(1) / per)) / (1.414 ** (2 / n) - 1)
    alpha = -beta + np.sqrt(beta ** 2 + 2 * beta)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    filt = _gauss((h + lo + c) / 3, alpha, n)
    ftr = _gauss(tr, alpha, n)
    hband = filt + ftr * float(p["mult"])
    r = _rsi(c, int(p["length_rsi"]))
    ls = int(p["length_stoch"])
    rr = r.rolling(ls).max() - r.rolling(ls).min()
    k = (100 * (r - r.rolling(ls).min()) / rr.where(rr > 0)).rolling(int(p["smooth_k"])).mean()
    le = (filt > filt.shift(1)) & (c > hband) & ((k > 80) | (k < 20))
    lx = (c < hband) & (c.shift(1) >= hband.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
