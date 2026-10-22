"""The EMA 30 / 60 gap against 0.3 x ATR 60, 5-minute bars, long only: the gap crossing up over the margin goes long, crossing down under minus the margin closes.
Port of FMZ strategy #489017 "Dual EMA Trend Following Quantitative Strategy" (onetrend Lite v1.0).

FMZ source id: 489017

Source
    https://www.fmz.com/strategy/489017 (PineScript v6, FMZ last modified 2025-04-01 10:59:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 139-180), EMA 30 / 60; margin 0.3 x ATR 60; short entry commented out
    crossover(emaFast - emaSlow, 0.3 atr60) -> entry Long;  crossunder(emaFast - emaSlow, -0.3 atr60) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry and the short close are commented out. Long only. No sizing code. FREQ = "5min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA gap crossings with an ATR margin.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
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

NAME = "fmz_489017_ema30_60_gap_atr_margin_cross_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "emaMarginATRMult": [0.3, 0.6],
    "emaFastLen": [30, 15],
}
DEFAULT_PARAMS = {"emaMarginATRMult": 0.3, "emaFastLen": 30, "emaSlowLen": 60, "emaMarginATRLen": 60}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    diff = (c.ewm(span=int(p["emaFastLen"]), adjust=False).mean()
            - c.ewm(span=int(p["emaSlowLen"]), adjust=False).mean())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    mg = float(p["emaMarginATRMult"]) * _rma(tr, int(p["emaMarginATRLen"]))
    le = (diff > mg) & (diff.shift(1) <= mg.shift(1))
    lx = (diff < -mg) & (diff.shift(1) >= -mg.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
