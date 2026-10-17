"""Bollinger re-entry in a mid-width band, 3-minute bars, long only: the close crossing back above the lower band (16, 3)
while the band width (per mille of the basis) is between 20 and 50 goes long; an 8 % target, the high crossing the upper
band or a close under the lower band closes the long.
Port of FMZ strategy #431394 "Bollinger Band Breakout Strategy" (Bollinger Bands BAT/USDT 30min).

FMZ source id: 431394

Source
    https://www.fmz.com/strategy/431394 (PineScript v4, FMZ last modified 2023-11-07 15:08:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 217-269), BB 16 / 3, width 20-50, TP 8 %
    entry = crossover(close, lower) and 20 < (upper - lower) / basis x 1000 < 50 -> entry long
    exit(limit = avg price x 1.08);  cross(high, upper) or close < lower -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target is a fixed fraction of the entry price: tp_stop 0.08. The close is written after the
      entry and acts on the position held at the bar's start. "Flat" follows the house target on
      bars. stdev is the population deviation. The time window is always true. Long only; Opposite
      entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). FREQ = "3min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percentage target.
    2 generic: PASS, Bollinger bands and their relative width.
    3 crypto-exchange-only: no (BAT/USDT in the title and the pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431394_bb_width_reentry_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [16, 32],
    "tp_pct": [8.0, 2.0],
}
DEFAULT_PARAMS = {"length": 16, "mult": 3.0, "bbw_hi": 50, "bbw_lo": 20, "tp_pct": 8.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = basis + p["mult"] * sd, basis - p["mult"] * sd
    bbw = (up - dn) / basis * 1000
    entry = ((c > dn) & (c.shift(1) <= dn.shift(1)) & (bbw < p["bbw_hi"]) & (bbw > p["bbw_lo"])).to_numpy()
    h1, u1 = h.shift(1), up.shift(1)
    out = (((h > up) & (h1 <= u1)) | ((h < up) & (h1 >= u1)) | (c < dn)).to_numpy()
    ov, hv = o.to_numpy(dtype=float), h.to_numpy(dtype=float)
    tp = float(p["tp_pct"]) / 100
    m = len(entry)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and hv[i] >= ov[entry_i] * (1 + tp):   # house target from the fill
            pos = 0
        start = pos
        if entry[i] and pos == 0:
            le[i], pos, entry_i = True, 1, i + 1
        if start == 1 and out[i]:
            lx[i], pos = True, 0
    return le, lx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
