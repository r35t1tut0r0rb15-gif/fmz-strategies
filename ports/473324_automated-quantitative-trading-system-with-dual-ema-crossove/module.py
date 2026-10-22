"""EMA 21 / 50 crossings, hourly bars: the cross up goes long, the cross down goes short; reversing. Each trade's 40 / 80-tick stop and target are set from its signal close, ported as ATR multiples.
Port of FMZ strategy #473324 "Automated Quantitative Trading System with Dual EMA Crossover and Risk Management" (EMA Crossover Strategy with SL & TP).

FMZ source id: 473324

Source
    https://www.fmz.com/strategy/473324 (PineScript v5, FMZ last modified 2024-11-29 11:20:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-132), EMA 21 / 50 (constants); stop 40 / target 80 ticks from the signal close
    crossover(ema21, ema50) -> entry Long, exit(stop = close - 40 ticks, limit = close + 80 ticks);  crossunder -> entry Short, exit(stop = close + 40 ticks, limit = close - 80 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 40 / 80 ticks are 4 / 8 at the 0.1 tick, ported as ATR multiples at the hourly reading (~150):
      0.0267 / 0.0533 ATR 14 of the signal bar, from its close. The levels are sent as fractions of the
      fill open; a level at or through it is marketable and closed one bar late (as #458256). Crossings
      alternate, so no repeat signal re-sends a bracket. REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). The equity share is not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples from the signal close.
    2 generic: PASS, EMA crossings with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_473324_ema21_50_cross_tick_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.0267, 1.0],
    "tp_atr": [0.0533, 2.0],
}
DEFAULT_PARAMS = {"sl_atr": 0.0267, "tp_atr": 0.0533, "atr_len": 14}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _signals(bars_df, p):
    c = bars_df["close"]
    a, b = c.ewm(span=21, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1))
    se = (a < b) & (a.shift(1) >= b.shift(1))
    atr = _atr(bars_df, p["atr_len"])
    ks, kt = float(p["sl_atr"]), float(p["tp_atr"])
    lvl = {"l_sl": c - ks * atr, "l_tp": c + kt * atr, "s_sl": c + ks * atr, "s_tp": c - kt * atr}
    return le, se, lvl


def _fracs(bars_df, le, lvl, k):
    """Signal-bar levels as fractions of the fill open (k = 1: read one bar after the signal)."""
    o = bars_df["open"]
    lf = le.shift(k, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(k) / o).where(lf, lvl["s_sl"].shift(k) / o - 1)
    tp_f = (lvl["l_tp"].shift(k) / o - 1).where(lf, 1 - lvl["s_tp"].shift(k) / o)
    return sl_f, tp_f


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    sl_f, tp_f = _fracs(bars_df, le, lvl, 1)
    through = (sl_f <= 0) | (tp_f <= 0)          # marketable at the fill: closed at the next open
    lx = le.shift(1, fill_value=False) & through & ~se
    sx = se.shift(1, fill_value=False) & through & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
