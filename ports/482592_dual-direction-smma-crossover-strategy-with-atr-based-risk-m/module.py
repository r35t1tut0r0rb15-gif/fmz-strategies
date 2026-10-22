"""Closes crossing the SMMA 17, 4-hour bars: a crossing up goes long with a fixed 1150-point target, a crossing down goes short with a 1500-point target, each from the signal close; the stop 0.75 ATR beyond the SMMA is re-sent every bar (pending); reversing.
Port of FMZ strategy #482592 "Dual-Direction-SMMA-Crossover-Strategy-with-ATR-Based-Risk-Management-and-Fixed-Take-Profit-双向SMMA交叉ATR风控定向获利策略" (SMMA 17 Crossover Strategy (Long & Short, ATR SL & Fixed TP)).

FMZ source id: 482592

Source
    https://www.fmz.com/strategy/482592 (PineScript v5, FMZ last modified 2025-02-19 10:59:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-151), SMMA 17; ATR rma(tr, 14) x 0.75; TP 1150 points long, 1500 points short; 200 % of equity
    crossover(close, smma) -> entry Long (TP = close + 1150);  crossunder -> entry Short (TP = close - 1500)
    every bar: exit Long (stop = smma - 0.75 atr, limit = TP);  crossunder -> close Long;  exit Short (stop = smma + 0.75 atr, limit = TP);  crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each crossing enters one side and closes the other: the close does not act on the position being
      reversed (as #441963), so the crossings reverse. The targets are price amounts, ported as fractions
      of 42000 of the signal close (2.738e-02 / 3.571e-02), sent as fractions of the fill open (a level at
      or through it is marketable and closed one bar late, as #458256). The stop follows the SMMA bar by
      bar: stops() cannot express a level re-set every bar, so it is described here and kept pending (as
      #438034, mark trailing_stop_pending). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. The 200 % of equity size is sizing.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; point targets as fractions of the fill; SMMA stop described (pending).
    2 generic: PASS, SMMA crossings with fixed targets.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482592_smma17_cross_point_target_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "smma_length": [17, 34],
    "tp_scale": [1.0, 2.0],
}
DEFAULT_PARAMS = {"smma_length": 17, "tp_scale": 1.0, "l_tp_frac": 2.738095e-02, "s_tp_frac": 3.571429e-02}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    sm = _rma(c, int(p["smma_length"]))                  # SMMA seeded by the SMA, as written
    le = (c > sm) & (c.shift(1) <= sm.shift(1))
    se = (c < sm) & (c.shift(1) >= sm.shift(1))
    k = float(p["tp_scale"])
    lvl = {"l_tp": c * (1 + float(p["l_tp_frac"]) * k), "s_tp": c * (1 - float(p["s_tp_frac"]) * k)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = lvl["l_tp"].shift(1) <= o                    # marketable at the fill
    s_thr = lvl["s_tp"].shift(1) >= o
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
