"""Kalman-smoothed Hull MAs with the WaveTrend cross, hourly bars: when the Kalman HMA3 crosses above
the Kalman HMA together with WT1 crossing above WT2 go long; the mirror goes short. Each position has a
5 % stop and a 10 % target.
Port of FMZ strategy #427921 "Trading Strategy Based on Hull Moving Average and WT Cross" (pigsq).

FMZ source id: 427921

Source
    https://www.fmz.com/strategy/427921 (PineScript v5, FMZ last modified 2023-09-26 20:00:32).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 235-351), WT 10 / 21, Hull 24 of hl2, gain 10000, SL 5 %, TP 10 %
    wt1 = ema(ci, 21) with ci = (hlc3 - ema(hlc3, 10)) / (0.015 ema(|hlc3 - esa|, 10)); wt2 = sma(wt1, 4)
    a = kahlman(hma(hl2, 24)); b = kahlman(hma3(close, 12)); kahlman: smooth + velocity, gain 1
    long = b crosses above a and crossover(wt1, wt2); short = a crosses above b and crossunder(wt1, wt2)
    exit(stop = avg x (1 -+ 5 %), limit = avg x (1 +- 10 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Defaults: WT cross on, second method off, Kalman on: the entries above. The else-if branches
      repeat the same conditions and never add an order. The closes coincide with the opposite
      entries (redundant with the reversal).
    * hma3 uses close (not the source input) and p = 12, as written.
    * The crosses are written as `x > y and x[1] < y[1]` (strict on both sides).
    * Percent-of-entry levels: sl_stop 0.05, tp_stop 0.10. The date window is open (999-9999).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, MA lengths and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427921_kalman_hull_wavetrend"
FAMILY = "hull_ma"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [24, 48],
    "sl_pct": [5.0, 2.5],
    "tp_pct": [10.0, 5.0],
}
DEFAULT_PARAMS = {"n1": 10, "n2": 21, "lookback": 24, "gain": 10000, "sl_pct": 5.0, "tp_pct": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    n = int(n)
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _kahlman(x, g):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    kf1, velo1 = np.nan, np.nan
    k = g / 10000
    for i in range(len(v)):
        base = v[i] if np.isnan(kf1) else kf1          # nz(kf[1], x)
        dk = v[i] - base
        smooth = base + dk * np.sqrt(k * 2)
        velo = (0.0 if np.isnan(velo1) else velo1) + k * dk
        out[i] = smooth + velo
        kf1, velo1 = out[i], velo
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ap = (h + lo + c) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    r = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * r)).ewm(span=int(p["n2"]), adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    L = int(p["lookback"])
    src = (h + lo) / 2
    hma = _wma(2 * _wma(src, L // 2) - _wma(src, L), int(round(np.sqrt(L))))
    q = L // 2
    hma3 = _wma(_wma(c, q // 3) * 3 - _wma(c, q // 2) - _wma(c, q), q)
    a, b = _kahlman(hma, p["gain"]), _kahlman(hma3, p["gain"])
    cross_up = (b > a) & (b.shift(1) < a.shift(1))
    cross_dn = (a > b) & (a.shift(1) < b.shift(1))
    wt_up = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))
    wt_dn = (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))
    long_e = (cross_up & wt_up).astype(bool)
    short_e = (cross_dn & wt_dn).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
