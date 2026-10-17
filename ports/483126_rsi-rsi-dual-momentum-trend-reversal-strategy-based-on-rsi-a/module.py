"""RSI 14 extremes confirmed by a stochastic-RSI %K / %D cross, 1-hour bars: RSI below 30 with %K below 20 crossing
above %D goes long; RSI above 70 with %K above 80 crossing below %D goes short; a long closes on RSI above 70 or %K
crossing below %D, a short on RSI below 30 or %K crossing above %D.
Port of FMZ strategy #483126 "基于RSI和随机RSI的双重动量趋势反转策略-Dual-Momentum-Trend-Reversal-Strategy-Based-on-RSI-and-Stochastic-RSI" (RSI + Stochastic RSI Strategy).

FMZ source id: 483126

Source
    https://www.fmz.com/strategy/483126 (PineScript v5, FMZ last modified 2025-02-27 16:53:04).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 107-159), RSI 14 (70 / 30), stoch RSI 14 smoothed 3 / 3 (80 / 20)
    long = rsi < 30 and k < 20 and crossover(k, d); longExit = rsi > 70 or crossunder(k, d)
    short = rsi > 70 and k > 80 and crossunder(k, d); shortExit = rsi < 30 or crossover(k, d)
    order: entry long, close long, entry short, close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stoch(rsi, rsi, rsi, 14) = 100 x (rsi - lowest rsi 14) / (highest rsi 14 - lowest rsi 14).
    * A long entry and its own exit never fall on one bar (the conditions exclude each other; shorts alike). A short
      signal while long also meets longExit: close + entry is a reversal, so only the entry is emitted (never an exit
      plus the opposite entry on one bar); the long side mirrored.
    * Entries reverse (REVERSAL INTENDED). No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and stochastic RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_483126_rsi_stochrsi_cross_reversal"
FAMILY = "oscillator_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stoch_os": [20, 30],
    "stoch_ob": [80, 70],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_ob": 70, "rsi_os": 30, "stoch_len": 14, "smooth_k": 3, "smooth_d": 3,
                  "stoch_ob": 80, "stoch_os": 20}


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
    rsi = _rsi(bars_df["close"], int(p["rsi_len"]))
    n = int(p["stoch_len"])
    lo, hi = rsi.rolling(n).min(), rsi.rolling(n).max()
    st = 100 * (rsi - lo) / (hi - lo)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    k_up = (k > d) & (k.shift(1) <= d.shift(1))
    k_dn = (k < d) & (k.shift(1) >= d.shift(1))
    long_e = ((rsi < p["rsi_os"]) & (k < p["stoch_os"]) & k_up).astype(bool)
    short_e = ((rsi > p["rsi_ob"]) & (k > p["stoch_ob"]) & k_dn).astype(bool)
    long_x = (((rsi > p["rsi_ob"]) | k_dn) & ~short_e).astype(bool)
    short_x = (((rsi < p["rsi_os"]) | k_up) & ~long_e).astype(bool)
    return long_e, long_x, short_e, short_x


def portfolio_kwargs(**params):
    return {}
