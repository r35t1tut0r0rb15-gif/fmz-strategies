"""Closes outside a band around the one-bar-back regression value, 4-hour bars: a close more than the gap under the 14-bar linear regression (offset 1) goes long, more than the gap above goes short;
reversing; each trade has a tick bracket; the tick gap and bracket are re-expressed as ATR multiples.
Port of FMZ strategy #439053 "Extreme Short term Scalping Strategy" (Extreme Scalping).

FMZ source id: 439053

Source
    https://www.fmz.com/strategy/439053 (PineScript v4, FMZ last modified 2024-01-17 12:06:39).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-190), linreg 14, offset 1; gap 100 ticks; fixed TP 300, SL 100 ticks; direction ALL
    out = linreg(close, 14, 1);  close < out - 100 ticks -> entry Long, exit(profit = 300, loss = 100);  close > out + 100 ticks -> entry Short, exit(profit = 300, loss = 100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the gap and the bracket are tick distances; the port uses the ATR(14) of the module's
      bars: the band is k_gap x ATR (signal bar) and sl_stop = k_sl x ATR / close of the signal bar
      (shifted one bar inside stops(), re-based on the fill) with a target 3 times it; 0.02 is the
      reading for both (100 ticks of 0.1 = 10 on BTC against a 4-hour ATR near 500), 0.5 a wider stop. The
      exit is re-sent on repeated signal bars with the same tick distances from the average price, so it
      stays fixed. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 4-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "4h" from the backtest
      header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick gap and bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439053_linreg_band_scalp_tick_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [0.02, 0.5],
    "k_gap": [0.02, 0.5],
}
DEFAULT_PARAMS = {"k_sl": 0.02, "k_gap": 0.02, "len": 14, "offset": 1, "atr_len": 14, "tp_ratio": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _linreg(y, n, offset=0):
    t = np.arange(n, dtype=float)

    def _fit(a):
        b, a0 = np.polyfit(t, a, 1)
        return a0 + b * (n - 1 - offset)

    return y.rolling(n).apply(_fit, raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    out = _linreg(c, int(p["len"]), int(p["offset"]))
    gap = float(p["k_gap"]) * _atr(bars_df, p["atr_len"])
    up = c < out - gap
    dn = c > out + gap
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_sl"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["tp_ratio"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
