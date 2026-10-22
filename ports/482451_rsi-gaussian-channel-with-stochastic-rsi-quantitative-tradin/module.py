"""An EMA 20 ± 2 standard-deviation channel with a Stochastic RSI (14 / 14, K 3), hourly bars, long only: the close crossing over the lower line together with K crossing over 20 buys; the close crossing over the upper line, or K crossing under 80, closes.
Port of FMZ strategy #482451 "基于高斯通道与随机RSI的量化交易策略优化系统-Gaussian-Channel-with-Stochastic-RSI-Quantitative-Trading-Strategy-Optimization-System" (Gaussian Channel with Stochastic RSI).

FMZ source id: 482451

Source
    https://www.fmz.com/strategy/482451 (PineScript v5, FMZ last modified 2025-02-18 15:00:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-132), EMA 20 +/- 2 sd ("Gaussian"); Stoch RSI 14 / 14, K 3, 20 / 80; 200 % of equity; commission 0.1 %; capital 10000
    crossover(close, lower) and crossover(k, 20) -> entry Long;  crossover(close, upper) or crossunder(k, 80) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "Gaussian" channel is an EMA with standard-deviation bands, as written; the stochastic is 0 when
      the RSI range is 0. The date filter always passes. Long only. The 200 % of equity size and capital
      are sizing; the commission is a cost and is not ported (house cost model). FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel re-entries with Stochastic RSI confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and capital stored, not ported; commission not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482451_ema20_sd_channel_reentry_stochrsi_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gc_length": [20, 50],
    "gc_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"gc_length": 20, "gc_mult": 2.0, "rsi_length": 14, "stoch_length": 14, "smooth_k": 3}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["gc_length"])
    mid = c.ewm(span=n, adjust=False).mean()
    sd = c.rolling(n).std(ddof=0)
    k_ = float(p["gc_mult"])
    up, dn = mid + k_ * sd, mid - k_ * sd
    r = _rsi(c, int(p["rsi_length"]))
    ns = int(p["stoch_length"])
    rl, rh = r.rolling(ns).min(), r.rolling(ns).max()
    st = (100 * (r - rl) / (rh - rl)).where(rh != rl, 0.0).where(rl.notna() & rh.notna())
    k = st.rolling(int(p["smooth_k"])).mean()
    le = (c > dn) & (c.shift(1) <= dn.shift(1)) & (k > 20) & (k.shift(1) <= 20)
    lx = ((c > up) & (c.shift(1) <= up.shift(1))) | ((k < 80) & (k.shift(1) >= 80))
    false = pd.Series(False, index=c.index)
    return le & ~lx, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
