"""EMA 21 / 55 crossings with an ATR bracket, 1-hour bars: the EMA 21 crossing over the EMA 55 goes long with a stop 1.5 ATR(14) under the signal close and a target 1 ATR over it; the mirror goes short;
reversing.
Port of FMZ strategy #439877 "Dual Moving Average Crossover Trading Strategy" (No-Nonsense Strategy Template [WM]).

FMZ source id: 439877

Source
    https://www.fmz.com/strategy/439877 (PineScript v3, FMZ last modified 2024-01-24 15:24:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 152-195), ATR 14; SL 1.5, TP1 1 (ATR multiples); EMA 21 / 55
    goLong = crossover(fast, slow) -> entry Long, exit(stop = close - 1.5 atr, limit = close + 1 atr);  goShort mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on the signal bar at levels from its close and stays in force: sl_stop = 1.5 x
      ATR(14) / close and tp_stop = 1 x ATR(14) / close of the signal bar, shifted one bar inside stops()
      and re-based on the fill. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, EMA crossings and ATR distances.
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

NAME = "fmz_439877_ema21_55_cross_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 3.0],
    "tp_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"sl_mult": 1.5, "tp_mult": 1.0, "fast": 21, "slow": 55, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_mult"]) * a).shift(1), "tp_stop": (float(p["tp_mult"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
