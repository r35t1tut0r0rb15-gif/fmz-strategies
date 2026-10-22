"""RSI 14 re-entries with MACD exits, 2-hour bars: the RSI crossing back under 70 goes short and back over 30 goes long; the MACD 12 / 26 crossing over its signal closes the short, crossing under closes the long; an opposite entry reverses.
Port of FMZ strategy #451706 "RSI与MACD结合的多空策略-RSI-and-MACD-Combined-Long-Short-Strategy" (RSI & MACD Strategy).

FMZ source id: 451706

Source
    https://www.fmz.com/strategy/451706 (PineScript v5, FMZ last modified 2024-05-17 11:04:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-164), RSI 14 (rma), levels 70 / 30; MACD 12 / 26 / 9 (EMA signal)
    crossunder(rsi, 70) -> entry Short;  crossover(macd, signal) -> close Short;  crossover(rsi, 30) -> entry Long;  crossunder(macd, signal) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in source order on each bar: an entry on the held side is ignored, an opposite
      entry reverses, and a close acts only on the trade held into the bar when no earlier call on the
      bar reversed it (a short closed by the MACD can be followed by the long entry on the same bar:
      one reversal). A held short meeting its own entry and its MACD close on one bar is closed (the
      entry is ignored as already held); a new short's close on its signal bar finds no trade.
      REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header
      (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI re-entries with MACD exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_451706_rsi_reentry_macd_cross_exit_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "ob": [70, 80],
    "os": [30, 20],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ob": 70.0, "os": 30.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    ob, os_ = float(p["ob"]), float(p["os"])
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    s_in = ((r < ob) & (r.shift(1) >= ob)).to_numpy()
    s_out = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    l_in = ((r > os_) & (r.shift(1) <= os_)).to_numpy()
    l_out = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        cur = pos
        if s_in[i] and cur != -1:
            cur = -1
        if s_out[i] and pos == -1 and cur == -1:
            cur = 0
        if l_in[i] and cur != 1:
            cur = 1
        if l_out[i] and pos == 1 and cur == 1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
