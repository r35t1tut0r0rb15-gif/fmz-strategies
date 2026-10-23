"""The Ultimate Oscillator 5 / 10 / 15 with a Williams-Alligator filter, 5-minute bars, long only: from flat, an up bar within 3 bars of the oscillator crossing over 45 (or 30) while the SMMA 20 of hl2 is above the SMMA 50 goes long; the oscillator crossing under 70, or a close 3 % under the entry with the oscillator under 70, closes.
Port of FMZ strategy #426617 "Long Reversal Strategy Based on Ultimate Oscillator" (Ultimate Oscillator [Long] Strategy).

FMZ source id: 426617

Source
    https://www.fmz.com/strategy/426617 (PineScript v4, FMZ last modified 2023-09-13 17:32:53).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 94-234), UO 5 / 10 / 15; buy line 45 (and 30), exit line 70; SMMA 20 / 50 of hl2; stop 3 % (close test); partial take-profit off; risk 10 % of capital
    longCond = crossover(UO, 45) or crossover(UO, 30);  close > open and barssince(longCond) <= 3 and position_size < 1 and smma(hl2, 20) > smma(hl2, 50) -> entry LEUO
    crossunder(UO, 70) -> close LEUO;  close < avg x 0.97 and UO < 70 -> close LEUO

Interpretation choices (Pine rules in SURVEY_README.md)
    * position_size < 1 is read as flat (the risk-based quantity is at least one unit on the source's
      instrument), so pyramiding 2 never adds. The partial exit is switched off (takeProfit false). The
      stop is a close test against the fill. The VWAP is computed but never used, so volume does not reach
      the orders: ported as not using volume (check 8). SMMA is the Alligator's (SMA seed, then Wilder).
      Long only. The risk-based quantity is sizing. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop.
    2 generic: PASS, Ultimate Oscillator turns with an Alligator trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 10 % / (close x 3 %), 20 % of equity, pyramiding 2 stored, not ported.
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

NAME = "fmz_426617_ultimate_oscillator_cross45_alligator_long_close_stop"
FAMILY = "oscillator_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_line": [45.0, 35.0],
    "exit_line": [70.0, 60.0],
}
DEFAULT_PARAMS = {"buy_line": 45.0, "exit_line": 70.0, "length1": 5, "length2": 10, "length3": 15, "stop": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _rma(x, n):
    """Wilder smoothing as Pine's rma (the Alligator SMMA): SMA seed, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _barssince(cond):
    """Pine barssince: bars since cond was last true (NaN before the first true)."""
    a = np.asarray(cond, dtype=bool)
    idx = np.maximum.accumulate(np.where(a, np.arange(len(a)), -1))
    return np.where(idx >= 0, np.arange(len(a)) - idx, np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    hi_ = pd.concat([h, pc], axis=1).max(axis=1, skipna=False)
    lo_ = pd.concat([lo, pc], axis=1).min(axis=1, skipna=False)
    bp, tr_ = c - lo_, hi_ - lo_
    avg = lambda n: bp.rolling(n).sum() / tr_.rolling(n).sum()
    uo = 100 * (4 * avg(int(p["length1"])) + 2 * avg(int(p["length2"])) + avg(int(p["length3"]))) / 7
    bl, xl = float(p["buy_line"]), float(p["exit_line"])
    long_cond = ((uo > bl) & (uo.shift(1) <= bl)) | ((uo > 30) & (uo.shift(1) <= 30))
    hl2 = (h + lo) / 2
    ok = (_rma(hl2, 20) > _rma(hl2, 50)).to_numpy()
    ent = (c > o).to_numpy() & (_barssince(long_cond.to_numpy()) <= 3) & ok
    x_uo = ((uo < xl) & (uo.shift(1) >= xl)).to_numpy()
    uo_lt = (uo < xl).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = float(p["stop"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill = 0, np.nan
    for i in range(m):
        if pos == 1 and (x_uo[i] or (cv[i] < fill * (1 - k) and uo_lt[i])):
            lx[i] = True
            pos = 0
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i] = True
            pos, fill = 1, ov[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
