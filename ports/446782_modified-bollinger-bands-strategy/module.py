"""Lower-band dips above the SMA 50 with a low stochastic RSI, 1-hour bars, long only: a close under the lower band (20, 2) but above the SMA 50 with the stochastic-RSI K under 20 goes long; a close over the
upper band closes.
Port of FMZ strategy #446782 "Modified Bollinger Bands Strategy" (Mod BB Strategy (Modified Bollinger Bands Strategy)).

FMZ source id: 446782

Source
    https://www.fmz.com/strategy/446782 (PineScript v5, FMZ last modified 2024-04-01 15:58:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 113-159), BB 20 / 2; SMA 50; stochastic RSI: RSI 14, stoch 14, K / D 3; oversold 20
    close < lower and close > sma50 and k < 20 -> entry Buy;  close > upper -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * k = sma(stoch(rsi, rsi, rsi, 14), 3), the stochastic of the RSI on itself; d only plots. Pine's
      stdev is the population deviation. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lower-band dips in an uptrend with a stochastic-RSI filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_446782_lower_band_above_sma50_stochrsi_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "oversold": [20.0, 10.0],
}
DEFAULT_PARAMS = {"length": 20, "oversold": 20.0, "mult": 2.0, "ma_len": 50, "k_len": 14, "d_len": 3, "rsi_len": 14}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    lower = basis - float(p["mult"]) * sd
    upper = basis + float(p["mult"]) * sd
    ma = c.rolling(int(p["ma_len"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    kn = int(p["k_len"])
    lo_r, hi_r = r.rolling(kn).min(), r.rolling(kn).max()
    st = 100 * (r - lo_r) / (hi_r - lo_r).where(hi_r > lo_r)
    k = st.rolling(int(p["d_len"])).mean()
    le = (c < lower) & (c > ma) & (k < float(p["oversold"]))
    lx = c > upper
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
