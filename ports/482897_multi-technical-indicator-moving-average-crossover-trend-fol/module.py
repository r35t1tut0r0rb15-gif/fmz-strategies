"""Bollinger re-entries confirmed by RSI, MACD and the stochastic, always in the market, 1-hour bars: RSI below 30,
MACD above its signal, %K below 20 and a close back above the middle band after the previous close was under the lower
band goes long; the mirror goes short.
Port of FMZ strategy #482897 "多重技术指标均线交叉趋势跟踪量化交易策略-Multi-Technical-Indicator-Moving-Average-Crossover-Trend-Following-Quantitative-Trading-Strategy" (TradingBot Strategy).

FMZ source id: 482897

Source
    https://www.fmz.com/strategy/482897 (PineScript v5, FMZ last modified 2025-02-20 16:56:38).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 142-184), RSI 14, BB 20 x 2, MACD 12 / 26 / 9, stochastic 14 / 3
    long = rsi < 30 and macd > signal and k < 20 and close > middle and close[1] < lower
    short = rsi > 70 and macd < signal and k > 80 and close < middle and close[1] > upper

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are as written (rare: a bar from below the lower band to above the middle with RSI still under
      30). The lot size is sizing: not ported. ta.bb uses the population standard deviation.
    * Entries reverse (REVERSAL INTENDED); no exits, no stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI, MACD, a stochastic and Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot size is quoted in original_sizing.txt and not ported.
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

NAME = "fmz_482897_bb_reentry_rsi_macd_stoch_reversal"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_os": [30, 40],
    "stoch_os": [20, 30],
}
DEFAULT_PARAMS = {"rsi_len": 14, "bb_len": 20, "k_len": 14, "rsi_os": 30, "stoch_os": 20}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    mid, dev = c.rolling(n).mean(), 2 * c.rolling(n).std(ddof=0)
    up, dn = mid + dev, mid - dev
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    kn = int(p["k_len"])
    ll, hh = lo.rolling(kn).min(), h.rolling(kn).max()
    k = 100 * (c - ll) / (hh - ll)
    os_, ss = p["rsi_os"], p["stoch_os"]
    long_e = ((rsi < os_) & (macd > sig) & (k < ss) & (c > mid) & (c.shift(1) < dn.shift(1))).astype(bool)
    short_e = ((rsi > 100 - os_) & (macd < sig) & (k > 100 - ss) & (c < mid) & (c.shift(1) > up.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
