"""The close crossing up through the lower EMA-stdev channel (20, 2) on the same bar as the stochastic RSI K crossing
up through 20 goes long; crossing the upper band or K crossing down through 80 closes it, long only, hourly bars.
Port of FMZ strategy #482451 "基于高斯通道与随机RSI的量化交易策略优化系统-Gaussian-Channel-with-Stochastic-RSI-Quantitative-Trading-Strategy-Optimization-System" (Gaussian Channel with Stochastic RSI).

FMZ source id: 482451

Source
    https://www.fmz.com/strategy/482451 (PineScript v5, FMZ last modified 2025-02-18 15:00:11).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 94-130), "Gaussian" channel = EMA 20 -/+ 2 stdev, RSI 14, stochastic 14,
K smoothing 3 (80 / 20)
    crossover(close, lower) and crossover(k, 20) -> entry long
    crossover(close, upper) or crossunder(k, 80) -> close long
    only from 2018-01-01 to 2069-01-01

Interpretation choices (Pine rules in SURVEY_README.md)
    * The channel named Gaussian is an EMA with a population stdev band (as written).
    * Clock rule (check 9 / C6): the date window is read as UTC; nothing trades before 2018-01-01.
    * Entries and closes cannot fall on one bar. Long only. Signal module, no stops. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an EMA-stdev channel and a stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity and the 0.1 % commission quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used; trading from 2018-01-01 00:00 UTC.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482451_ema_stdev_channel_stoch_rsi_cross_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "gc_mult": [2.0, 1.5],
    "gc_length": [20, 40],
}
DEFAULT_PARAMS = {"gc_length": 20, "gc_mult": 2.0, "rsi_len": 14, "stoch_len": 14, "smooth_k": 3,
                  "os": 20.0, "ob": 80.0}
START = pd.Timestamp("2018-01-01", tz="UTC")


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["gc_length"])
    mid = c.ewm(span=n, adjust=False).mean()
    sd = c.rolling(n).std(ddof=0)
    upper, lower = mid + p["gc_mult"] * sd, mid - p["gc_mult"] * sd
    rsi = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    lo_r, hi_r = rsi.rolling(sn).min(), rsi.rolling(sn).max()
    st = ((rsi - lo_r) / (hi_r - lo_r) * 100).where(hi_r != lo_r, 0.0)
    k = st.rolling(int(p["smooth_k"])).mean()

    def xover(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    live = pd.Series(bars_df.index >= START, index=bars_df.index)
    os_l = pd.Series(p["os"], index=c.index)
    ob_l = pd.Series(p["ob"], index=c.index)
    long_e = (xover(c, lower) & xover(k, os_l) & live).astype(bool)
    long_x = ((xover(c, upper) | xover(ob_l, k)) & live).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
