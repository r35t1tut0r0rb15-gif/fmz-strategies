"""The EMA 30 / 60 gap against an ATR 60 margin (0.3 x when ADX 14 is over 20, else 0.1 x), hourly bars, long only: the gap over the margin goes long, under minus the margin closes.
Port of FMZ strategy #489311 "Dynamic Trend Identification Strategy with Exponential Moving Average and Adaptive Volatility Threshold" (OneTrend Lite EMA).

FMZ source id: 489311

Source
    https://www.fmz.com/strategy/489311 (PineScript v6, FMZ last modified 2025-04-03 13:08:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-205), EMA 30 / 60; ATR 60; ADX 14 / 20 (hand-built); margins 0.3 / 0.1; 100 % of equity
    emaBull = ema30 - ema60 > m x atr60 -> entry Long;  emaBear = ema30 - ema60 < -m x atr60 -> close Long;  m = adx > 20 ? 0.3 : 0.1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry and exit are states. The ADX is the script's own (rma of DX over rma of DMs and true
      range). Its DG489311 partner #490075 is read on its own. Long only. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA gap states with an ADX-dependent ATR margin.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG489311 (2 members, best partner #490075, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489311_ema30_60_gap_adx_atr_margin_state_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atrMultStrong": [0.3, 0.6],
    "emaFastLen": [30, 15],
}
DEFAULT_PARAMS = {"atrMultStrong": 0.3, "emaFastLen": 30, "emaSlowLen": 60, "atrLen": 60, "adxLen": 14,
                  "adxThreshold": 20, "atrMultWeak": 0.1}


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
    tr_na = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr = tr_na.copy()
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index)
    n = int(p["adxLen"])
    trur = _rma(tr_na, n)
    pdi, mdi = 100 * _rma(pdm, n) / trur, 100 * _rma(mdm, n) / trur
    s = pdi + mdi
    dx = 100 * (pdi - mdi).abs() / s.where(s != 0)
    adx = _rma(dx, n)
    mult = pd.Series(np.where(adx > float(p["adxThreshold"]), float(p["atrMultStrong"]),
                              float(p["atrMultWeak"])), index=c.index)
    atr = _rma(tr, int(p["atrLen"]))
    le = diff > mult * atr
    lx = (diff < -mult * atr) & ~le
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
