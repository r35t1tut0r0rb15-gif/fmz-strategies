"""Internal bar strength reversion: a close in the bottom 5 % of the bar's range goes long, in the
top 1 % goes short; each trade has a tiny tick target (10) and stop (2).
Port of FMZ strategy #426145 "Internal Bar Strength Indicator Reversion system".

Source
    https://www.fmz.com/strategy/426145 (PineScript v5, FMZ last modified 2023-09-08 16:33:39).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 50-64)
    ibs = (close - low) / (high - low) * 100
    ibs < 5 -> entry long;  ibs > 99 -> entry short;  exit(profit = 10 ticks, loss = 2 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 10 / 2 ticks are instrument-specific (0.10 / 0.02 USD on BTC). They become
      5 sl_atr / sl_atr x ATR(14) at the signal bar (the source's 5:1 ratio), as tp_stop / sl_stop
      fractions shifted one bar inside stops().
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426145_ibs_extreme_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "ibs_low": [5, 10],
    "ibs_high": [95, 99],
    "sl_atr": [0.25, 0.5, 1.0],
}
DEFAULT_PARAMS = {"ibs_low": 5, "ibs_high": 99, "sl_atr": 0.25}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _signals(bars_df, p):
    h, l, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ibs = (c - l) / (h - l) * 100
    return (ibs < p["ibs_low"]).to_numpy(), (ibs > p["ibs_high"]).to_numpy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(up, index=idx), false.copy(), pd.Series(dn & ~up, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    sig = pd.Series(up | dn, index=bars_df.index)
    frac = (p["sl_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(sig)
    return {"sl_stop": frac.shift(1), "tp_stop": (5 * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
