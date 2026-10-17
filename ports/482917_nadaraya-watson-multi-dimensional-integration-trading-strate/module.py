"""A weighted blend of four kernel-smoothed series (price, RSI, ATR / price, distance from SMA 50) crossing its own
10-bar SMA, filtered by SMA 200 and RSI 50, with a 1.5 % stop / 3 % target from the entry, 1-minute bars.
Port of FMZ strategy #482917 "基于Nadaraya-Watson的多维度整合交易策略-Multi-Dimensional-Integration-Trading-Strategy-Based-on-Nadaraya-Watson" (Enhanced Multidimensional Integration Strategy with Nadaraya).

FMZ source id: 482917

Source
    https://www.fmz.com/strategy/482917 (PineScript v5, FMZ last modified 2025-02-27 17:21:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 112-213), weights 0.4 / 0.2 / 0.2 / 0.2, smoothing 20, bandwidth 20, SMA 200,
RSI level 50, SL 1.5 %, TP 3 %
    nadaraya(src) = sum_i w_i src[i] / sum_i w_i, w_i = exp(-0.5 ((len - 1 - i) / bw)^2), i = 0..19 (na before bar 20)
    integrated = 0.4 sm(close) + 0.2 sm(rsi / 100) + 0.2 sm(atr / close) + 0.2 sm((close - sma50) / close)
    long = crossover(integrated, sma(integrated, 10)) and close > sma200 and rsi > 50 (short mirrored)
    while held: exit(stop / limit = avg_price x (1 -+ 1.5 %) / (1 +- 3 %)) on every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel weights are as written (the heaviest weight on the OLDEST bar of the window).
    * The blend is dominated by the price term (it is not scale-free), as written; crosses of its own SMA are what the
      rule uses.
    * The exits use strategy.position_avg_price (the fill) on every bar while held: a fixed 1.5 % / 3 % bracket from
      the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a fixed bracket from the fill.
    2 generic: PASS, smoothed price / RSI / ATR / distance blend crossing its own average, percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482917_kernel_blend_cross_trend_rsi_bracket"
FAMILY = "kernel_regression"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.5, 1.0],
    "tp_pct": [3.0, 2.0],
}
DEFAULT_PARAMS = {"smooth_len": 20, "bw": 20.0, "trend_len": 200, "rsi_level": 50, "sl_pct": 1.5, "tp_pct": 3.0}

WEIGHTS = (0.4, 0.2, 0.2, 0.2)


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _nadaraya(s, n, bw):
    """sum_i w_i s[t - i] / sum_i w_i with w_i = exp(-0.5 ((n - 1 - i) / bw)^2); na before bar n."""
    w = np.exp(-0.5 * ((n - 1 - np.arange(n)) / bw) ** 2)      # w[i] multiplies the value i bars back
    v = s.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) > n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)[:, ::-1]   # column i = i bars back
        out[n - 1:] = (win * w).sum(axis=1) / w.sum()
        out[:n] = np.nan                                         # bar_index < len -> na
    return pd.Series(out, index=s.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n, bw = int(p["smooth_len"]), float(p["bw"])
    rsi = _rsi(c, 14)
    series = (c, rsi / 100, _atr(bars_df, 14) / c, (c - c.rolling(50).mean()) / c)
    integ = sum(wt * _nadaraya(s, n, bw) for wt, s in zip(WEIGHTS, series))
    avg = integ.rolling(10).mean()
    trend = c.rolling(int(p["trend_len"])).mean()
    lvl = p["rsi_level"]
    long_e = ((integ > avg) & (integ.shift(1) <= avg.shift(1)) & (c > trend) & (rsi > lvl)).astype(bool)
    short_e = ((integ < avg) & (integ.shift(1) >= avg.shift(1)) & (c < trend) & (rsi < lvl)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
