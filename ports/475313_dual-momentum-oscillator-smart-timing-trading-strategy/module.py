"""RSI and stochastic lows, hourly bars, long only: RSI 14 under 35 with the smoothed stochastic %K (14, 3) under 20 buys; RSI over 70 with %K over 80 sells.
Port of FMZ strategy #475313 "Dual Momentum Oscillator Smart Timing Trading Strategy" (BTC Buy & Sell Strategy (RSI & Stoch RSI)).

FMZ source id: 475313

Source
    https://www.fmz.com/strategy/475313 (PineScript v5, FMZ last modified 2024-12-17 14:36:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-151), RSI 14, 35 / 70; stochastic 14, K 3, D 3, 20 / 80; weekly data off
    rsi < 35 and k < 20 -> entry Long;  rsi > 70 and k > 80 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Use Weekly Data" off the requests are the chart itself. The "stochastic RSI" is the
      stochastic of price (ta.stoch(close, high, low, 14)), as written. The entry and close cannot hold
      on one bar. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI / stochastic extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG475313 (2 members, best partner #475632, Jaccard 0.912); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475313_rsi35_stoch20_dip_rsi70_stoch80_exit_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_buy": [35, 30],
    "stoch_buy": [20, 10],
}
DEFAULT_PARAMS = {"rsi_buy": 35, "stoch_buy": 20, "rsi_sell": 70, "stoch_sell": 80}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, 14)
    k = (100 * (c - lo.rolling(14).min()) / (h.rolling(14).max() - lo.rolling(14).min())).rolling(3).mean()
    le = (r < float(p["rsi_buy"])) & (k < float(p["stoch_buy"]))
    lx = (r > float(p["rsi_sell"])) & (k > float(p["stoch_sell"]))
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
