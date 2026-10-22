"""Gaussian channel (period 144, 4 poles, x 1.414) breakouts in season, 4-hour bars, long only: a close above the upper band while the filter rises and the Stochastic RSI is at or above 80, in September to February, buys; the close crossing under the lower band closes.
Port of FMZ strategy #481093 "Momentum Adaptive Gaussian Channel Multi Period Strategy" (Demo GPT - Gold Gaussian Strategy).

FMZ source id: 481093

Source
    https://www.fmz.com/strategy/481093 (PineScript v6, FMZ last modified 2025-02-08 14:49:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 93-229), Gaussian period 144, poles 4, multiplier 1.414; Stochastic RSI 14 / 14, K 3, level 80; season Sep-Feb; ATR 22 risk sizing; commission 0.1 %
    beta / alpha from the period and poles;  lag = (144 - 1) / 8;  src = hlc3 + (hlc3 - hlc3[lag]);  main = 4-pole recursive filter of src;  tr filter of ta.tr(true);  bands = main +/- 1.414 x tr filter
    main > main[1] and close > upper and stochK >= 80 and month in Sep..Dec or Jan..Feb -> entry Long (qty from risk);  crossunder(close, lower) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop runs the 4-pole recursive filter as written: the source is nz()'d, so it starts from 0 while
      the lagged hlc3 is na and converges from there; ta.tr(true) uses the high - low on the first bar.
      The season uses the bar's UTC month (the header market's exchange time). Long only. The risk-based
      qty is sizing; the commission setting is a cost and is not ported (house cost model). FREQ = "4h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Gaussian-channel breakouts with Stochastic RSI and a seasonal filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk 0.5 % / ATR 22 qty stored, not ported; commission not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: season by UTC month (Sep-Feb).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481093_gaussian144_channel_breakout_stochrsi_season_long"
FAMILY = "volatility_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_gc": [144, 89],
    "multiplier": [1.414, 2.0],
}
DEFAULT_PARAMS = {"length_gc": 144, "multiplier": 1.414, "poles": 4, "smooth_k": 3, "rsi_length": 14,
                  "stoch_length": 14, "overbought": 80, "start_month": 9, "end_month": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    n, poles = int(p["length_gc"]), int(p["poles"])
    beta = (1 - np.cos(4 * np.arcsin(1) / n)) / (1.414 ** (2 / poles) - 1)
    alpha = -beta + np.sqrt(beta ** 2 + 2 * beta)
    lag = int((n - 1) / (2 * poles))
    hlc3 = (h + lo + c) / 3
    src = hlc3 + (hlc3 - hlc3.shift(lag))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # ta.tr(true)
    main = pd.Series(_gauss(src, alpha, poles), index=c.index)
    trf = pd.Series(_gauss(tr, alpha, poles), index=c.index)
    k = float(p["multiplier"])
    upper, lower = main + trf * k, main - trf * k
    r = _rsi(c, int(p["rsi_length"]))
    ns = int(p["stoch_length"])
    rl, rh = r.rolling(ns).min(), r.rolling(ns).max()
    stoch_k = (100 * (r - rl) / (rh - rl).where(rh > rl)).rolling(int(p["smooth_k"])).mean()
    mon = pd.Series(c.index.tz_convert("UTC").month, index=c.index)
    season = (mon >= int(p["start_month"])) | (mon <= int(p["end_month"]))
    le = (main > main.shift(1)) & (c > upper) & (stoch_k >= float(p["overbought"])) & season
    lx = (c < lower) & (c.shift(1) >= lower.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
