"""Ten-minute bars: a price stochastic (14, smoothed 3) crossing over the stochastic-RSI D line while the stochastic-RSI K is under 20 and the RSI 14 crosses over 30 goes long; the price stochastic crossing under that D line above 80 with the RSI crossing under 70 goes short; reversing.
Port of FMZ strategy #433958 "Oscillation Positioning Breakthrough Strategy with Multiple Indicators" (Stoch.RSI+RSI+DoubleStrategy+CMWilliamsVixFix+MFI).

FMZ source id: 433958

Source
    https://www.fmz.com/strategy/433958 (PineScript v3, FMZ last modified 2023-12-01 17:49:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 220-263), stochastic RSI 14 / 14 / 3 / 3; price stochastic 14 / 3; RSI 14 at 30 / 70; stochastic 80 / 20
    ks = sma(stoch(close, high, low, 14), 3);  ds = sma(k, 3) (k = the stochastic-RSI K);  crossover(ks, ds) and k < 20 and crossover(rsi, 30) -> entry LONG
    crossunder(ks, ds) and ks > 80 and crossunder(rsi, 70) -> entry SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * ds is the 3-bar SMA of the stochastic-RSI K, not of ks, as written, so the "double strategy" crosses
      the price stochastic against a stochastic-RSI line (weird case). The long test requires both lines
      defined; the short test reads ks > 80 itself. The Williams Vix Fix and the MFI only feed plots:
      volume is not used. No exits: the opposite entry reverses. REVERSAL INTENDED. No sizing code. FREQ =
      "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic and RSI oversold / overbought crossings.
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

NAME = "fmz_433958_price_stoch_vs_stochrsi_d_rsi_cross_10m_reversal"
FAMILY = "stochastic_rsi"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_stoch": [14, 21],
    "smooth_k": [3, 5],
}
DEFAULT_PARAMS = {"length_stoch": 14, "smooth_k": 3, "smooth_d": 3, "rsi_len": 14,
                  "stoch_ob": 80.0, "stoch_os": 20.0, "rsi_ob": 70.0, "rsi_os": 30.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ns, sk, sd = int(p["length_stoch"]), int(p["smooth_k"]), int(p["smooth_d"])
    r = _rsi(c, int(p["rsi_len"]))
    rl, rh = r.rolling(ns).min(), r.rolling(ns).max()
    k = (100 * (r - rl) / (rh - rl).where(rh != rl)).rolling(sk).mean()
    ll, hh = lo.rolling(ns).min(), h.rolling(ns).max()
    ks = (100 * (c - ll) / (hh - ll).where(hh != ll)).rolling(sk).mean()
    ds = k.rolling(sd).mean()
    up_x = (ks > ds) & (ks.shift(1) <= ds.shift(1))
    dn_x = (ks < ds) & (ks.shift(1) >= ds.shift(1))
    r_up = (r > float(p["rsi_os"])) & (r.shift(1) <= float(p["rsi_os"]))
    r_dn = (r < float(p["rsi_ob"])) & (r.shift(1) >= float(p["rsi_ob"]))
    long_c = ks.notna() & ds.notna() & up_x & (k < float(p["stoch_os"])) & r_up
    short_c = dn_x & (ks > float(p["stoch_ob"])) & r_dn
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return long_c & ~short_c, false, short_c, false.copy()


def portfolio_kwargs(**params):
    return {}
