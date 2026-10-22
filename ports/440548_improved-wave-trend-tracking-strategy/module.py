"""WaveTrend level crossings, 1-hour bars: the WaveTrend line crossing over 53 goes long, crossing under -60 goes short (reversing); a bar reaching 1 % above or 0.5 % below the entry closes a long
(mirrored for shorts), tested on the bar and sent at the next open.
Port of FMZ strategy #440548 "Improved Wave Trend Tracking Strategy" (Nique Audi).

FMZ source id: 440548

Source
    https://www.fmz.com/strategy/440548 (PineScript v5, FMZ last modified 2024-01-31 15:35:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-250), WaveTrend 10 / 21 on hlc3; levels 60 / 53, -65 / -60; target 1 %, stop 0.5 %
    wt1 = ema((hlc3 - esa) / (0.015 d), 21);  crossover(wt1, 53) -> entry Long;  crossunder(wt1, -60) -> entry Short
    long held and high >= avg price x 1.01 or low <= avg price x 0.995 -> close Long;  short held and low <= avg price x 0.99 or high >= avg price x 1.005 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target and stop are bar tests against the fill price, sent as closes at the next open (not
      orders). A close acts only on the held position; one after a reversing entry leaves the reversal
      standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-tested target and stop.
    2 generic: PASS, WaveTrend level crossings.
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

NAME = "fmz_440548_wavetrend_level_cross_bar_tests"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_pct": [1.0, 2.0],
    "sl_pct": [0.5, 1.0],
}
DEFAULT_PARAMS = {"tp_pct": 1.0, "sl_pct": 0.5, "n1": 10, "n2": 21, "ob2": 53, "os2": -60}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ap = (h + lo + c) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d.where(d > 0))).ewm(span=int(p["n2"]), adjust=False).mean()
    ob, os_ = float(p["ob2"]), float(p["os2"])
    L = ((wt1 > ob) & (wt1.shift(1) <= ob)).to_numpy()
    S = ((wt1 < os_) & (wt1.shift(1) >= os_)).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp_pct"]) / 100, float(p["sl_pct"]) / 100
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    pos, x = 0, np.nan
    for i in range(m):
        new = pos
        if L[i]:
            new = 1
        if S[i]:
            new = -1
        if pos == 1 and new == 1 and (hv[i] >= x * (1 + tp) or lv[i] <= x * (1 - sl)):
            new = 0
        if pos == -1 and new == -1 and (lv[i] <= x * (1 - tp) or hv[i] >= x * (1 + sl)):
            new = 0
        if new != 0 and new != pos and i + 1 < m:
            x = ov[i + 1]                                # the fill of the new position
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
