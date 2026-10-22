"""Stochastic RSI (RSI 14, stochastic 14, K 3, D 3) K / D crossings in the outer bands, 4-hour bars: K crossing over D under 20 goes long, crossing under D over 80 goes short; reversing.
Port of FMZ strategy #476262 "Adaptive Trading Strategy Based on Stochastic RSI Dual Line Crossover" (Stochastic RSI Strategy).

FMZ source id: 476262

Source
    https://www.fmz.com/strategy/476262 (PineScript v5, FMZ last modified 2024-12-27 15:06:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-182), RSI 14; stochastic 14; smooth K 3, D 3; bands 20 / 80; date filter always true
    k = sma(stoch(rsi, rsi, rsi, 14), 3), d = sma(k, 3);  crossover(k, d) and k < 20 -> close Short, entry Long;  crossunder(k, d) and k > 80 -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each signal closes the opposite position and enters, which is a reversal. A zero stochastic range
      gives na (no signal), as Pine's division. The d_period input is unused. REVERSAL INTENDED. No
      sizing code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Stochastic RSI crossings in the outer bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_476262_stoch_rsi14_kd_cross_band_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "k_period": [14, 21],
    "lower_band": [20, 10],
}
DEFAULT_PARAMS = {"k_period": 14, "lower_band": 20, "rsi_length": 14, "smooth_k": 3, "smooth_d": 3}


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
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["k_period"])
    lo_r, hi_r = r.rolling(n).min(), r.rolling(n).max()
    rng = (hi_r - lo_r).where(hi_r > lo_r)
    st = 100 * (r - lo_r) / rng
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    lb = float(p["lower_band"])
    le = (k > d) & (k.shift(1) <= d.shift(1)) & (k < lb)
    se = (k < d) & (k.shift(1) >= d.shift(1)) & (k > 100 - lb)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
