"""Gaussian channel (period 144, 4 poles, x 1.414) breakouts with the Stochastic RSI at an extreme, broker days, long only: a close above the upper band while the filter rises and K is at or above 80 or at or under 20 buys; the close crossing back under the upper band closes.
Port of FMZ strategy #482426 "多周期高斯通道结合StochRSI趋势跟踪策略-Multi-Period-Gaussian-Channel-with-StochRSI-Trend-Following-Strategy" (Demo GPT - Gaussian Channel Strategy v3.0).

FMZ source id: 482426

Source
    https://www.fmz.com/strategy/482426 (PineScript v5, FMZ last modified 2025-02-18 13:50:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-208), Gaussian hlc3, poles 4, period 144, multiplier 1.414 (reduced-lag and fast modes off); Stoch RSI 14 / 14, K 3; 250 % of equity; commission 0.1 %
    main = 4-pole recursive filter of hlc3;  tr filter of ta.tr(true);  bands = main +/- 1.414 x tr filter;  main > main[1] and close > upper and (k >= 80 or k <= 20) -> entry Long;  crossunder(close, upper) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop runs the 4-pole recursive filter as written (its state starts at 0); the reduced-lag and
      fast-response modes are off by default. Long only. The 250 % of equity size is sizing; the
      commission setting is a cost and is not ported (house cost model). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Gaussian-channel breakouts with a Stochastic RSI extreme filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 250 % of equity stored, not ported; commission not ported.
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

NAME = "fmz_482426_gaussian144_breakout_stochrsi_extreme_long"
FAMILY = "volatility_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sampling_period": [144, 89],
    "multiplier": [1.414, 2.0],
}
DEFAULT_PARAMS = {"sampling_period": 144, "multiplier": 1.414, "poles": 4, "rsi_length": 14, "stoch_length": 14, "k_smooth": 3}


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


def _gauss(src, alpha, poles):
    """f_filt9x: f = alpha^N nz(src) + sum_k (-1)^(k+1) C(N, k) (1 - alpha)^k nz(f[k])."""
    v = np.nan_to_num(np.asarray(src, dtype=float), nan=0.0)
    x = 1 - alpha
    binom = [1]
    for k in range(1, poles + 1):
        binom.append(binom[-1] * (poles - k + 1) // k)
    coef = [(-1) ** (k + 1) * binom[k] * x ** k for k in range(1, poles + 1)]
    out = np.zeros(len(v))
    an = alpha ** poles
    for i in range(len(v)):
        f = an * v[i]
        for k in range(1, poles + 1):
            if i - k >= 0:
                f += coef[k - 1] * out[i - k]
        out[i] = f
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, poles = int(p["sampling_period"]), int(p["poles"])
    beta = (1 - np.cos(4 * np.arcsin(1) / n)) / (1.414 ** (2 / poles) - 1)
    alpha = -beta + np.sqrt(beta ** 2 + 2 * beta)
    hlc3 = (h + lo + c) / 3
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # ta.tr(true)
    main = pd.Series(_gauss(hlc3, alpha, poles), index=c.index)
    trf = pd.Series(_gauss(tr, alpha, poles), index=c.index)
    upper = main + trf * float(p["multiplier"])
    r = _rsi(c, int(p["rsi_length"]))
    ns = int(p["stoch_length"])
    rl, rh = r.rolling(ns).min(), r.rolling(ns).max()
    k = (100 * (r - rl) / (rh - rl).where(rh > rl)).rolling(int(p["k_smooth"])).mean()
    le = (main > main.shift(1)) & (c > upper) & ((k >= 80) | (k <= 20))
    lx = (c < upper) & (c.shift(1) >= upper.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
