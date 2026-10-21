"""Noro's SuperTrend pullbacks, 1-hour bars: with the SuperTrend (3 x ATR 7) up, a down candle buys; with it down, an up candle sells; reversing.
Port of FMZ strategy #437759 "Trend Following Momentum Breakout Strategy" (ST str 1.0).

FMZ source id: 437759

Source
    https://www.fmz.com/strategy/437759 (PineScript v2, FMZ last modified 2024-01-05 13:38:18).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 136-189), SuperTrend factor 3, ATR 7; cloud 25 % (plotted only); long and short on; date range wide
    TUp = close[1] > TUp[1] ? max(hl2 - 3 atr, TUp[1]) : hl2 - 3 atr;  TDown mirror;  Trend = close > TDown[1] ? 1 : close < TUp[1] ? -1 : Trend[1]
    up = Trend == 1 and close < open -> entry Long;  dn = Trend == -1 and close > open -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SuperTrend is the script's own recursion (atr = Wilder ATR 7); comparisons with the not yet
      defined lines are false and the trend starts at 1 (nz). The cloud, centre and border lines are
      plotted only. REVERSAL INTENDED. The lot is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR SuperTrend side and candle colour.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity-based lot and capital % stored.
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

NAME = "fmz_437759_noro_supertrend_pullback"
FAMILY = "supertrend"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_len": [7, 14],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_len": 7}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    f = float(p["factor"])
    m = len(cv)
    tup, tdn = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            up_, dn_ = hl2[i] - f * atr[i], hl2[i] + f * atr[i]
            c1 = cv[i - 1] if i else np.nan
            tu1 = tup[i - 1] if i else np.nan
            td1 = tdn[i - 1] if i else np.nan
            tup[i] = (np.nan if np.isnan(up_) or np.isnan(tu1) else max(up_, tu1)) if c1 > tu1 else up_
            tdn[i] = (np.nan if np.isnan(dn_) or np.isnan(td1) else min(dn_, td1)) if c1 < td1 else dn_
            t1 = trend[i - 1] if i else 1.0
            trend[i] = 1.0 if cv[i] > td1 else (-1.0 if cv[i] < tu1 else t1)
    lc = (trend == 1) & (cv < ov)
    sc = (trend == -1) & (cv > ov)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(lc, index=ix), false, pd.Series(sc, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
