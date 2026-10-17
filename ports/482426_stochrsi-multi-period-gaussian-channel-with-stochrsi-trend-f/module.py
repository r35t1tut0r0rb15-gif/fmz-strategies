"""Closes above a rising four-pole Gaussian channel (period 144, 1.414 x the filtered true range) with the stochastic
RSI at an extreme (>= 80 or <= 20) go long; a close crossing back under the upper band closes it, long only, daily
bars.
Port of FMZ strategy #482426 "多周期高斯通道结合StochRSI趋势跟踪策略-Multi-Period-Gaussian-Channel-with-StochRSI-Trend-Following-Strategy" (Demo GPT - Gaussian Channel Strategy v3.0).

FMZ source id: 482426

Source
    https://www.fmz.com/strategy/482426 (PineScript v5, FMZ last modified 2025-02-18 13:50:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-195), source hlc3, poles 4, period 144, multiplier 1.414, stochastic
RSI 14 / 14 / 3 / 3
    beta = (1 - cos(2 pi / 144)) / (1.414^(2 / 4) - 1); alpha = -beta + sqrt(beta^2 + 2 beta)
    filt = the 4-pole recursive filter f_filt9x(alpha, hlc3, 4); trFilt the same on ta.tr(true)
    upper = filt + 1.414 trFilt
    filt > filt[1] and close > upper and (k >= 80 or k <= 20) -> entry long; crossunder(close, upper) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pole filter is the source's recursion with nz() (values before the first bar are 0), as written; the
      reduced-lag and fast-response options are off by default. The date inputs are unused (timeCondition = true).
    * Entries and closes cannot fall on one bar. Long only. Signal module, no stops. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a recursive price filter, a filtered true range and a stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity and the 0.1 % commission quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd
from math import comb

NAME = "fmz_482426_ehlers_gaussian_channel_break_stoch_rsi_long"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [144, 72],
    "multiplier": [1.414, 2.0],
}
DEFAULT_PARAMS = {"poles": 4, "period": 144, "multiplier": 1.414, "rsi_len": 14, "stoch_len": 14, "k_len": 3}


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


def _pole_filter(src, a, poles):
    """f_filt9x: f = a^n s + sum_k (-1)^(k+1) C(n, k) (1 - a)^k f[k] (nz: 0 before the first bar)."""
    x = 1 - a
    s = np.nan_to_num(np.asarray(src, dtype=float))
    m = len(s)
    f = np.zeros(m)
    for t in range(m):
        acc = a ** poles * s[t]
        for k in range(1, poles + 1):
            prev = f[t - k] if t - k >= 0 else 0.0
            acc += (-1) ** (k + 1) * comb(poles, k) * x ** k * prev
        f[t] = acc
    return f


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    poles, per = int(p["poles"]), int(p["period"])
    beta = (1 - np.cos(4 * np.arcsin(1) / per)) / (1.414 ** (2 / poles) - 1)
    alpha = -beta + np.sqrt(beta ** 2 + 2 * beta)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]          # ta.tr(true)
    filt = pd.Series(_pole_filter(((h + lo + c) / 3).to_numpy(), alpha, poles), index=c.index)
    trf = pd.Series(_pole_filter(tr.to_numpy(), alpha, poles), index=c.index)
    upper = filt + trf * p["multiplier"]
    rsi = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    rl, rh = rsi.rolling(sn).min(), rsi.rolling(sn).max()
    k = (100 * (rsi - rl) / (rh - rl)).rolling(int(p["k_len"])).mean()
    long_e = ((filt > filt.shift(1)) & (c > upper) & ((k >= 80) | (k <= 20))).astype(bool)
    long_x = ((c < upper) & (c.shift(1) >= upper.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
