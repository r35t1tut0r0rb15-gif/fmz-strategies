"""RSI 9 divergences, long only, 1-hour bars: a pivot low of the RSI (1 / 3) with a regular or hidden bullish divergence against the previous pivot low goes long; the RSI crossing over 80 or a regular
bearish divergence at a pivot high closes.
Port of FMZ strategy #439954 "RSI多空分歧指标The-RSI-Divergence-Indicator-Strategy" (RSI Divergence Indicator).

FMZ source id: 439954

Source
    https://www.fmz.com/strategy/439954 (PineScript v4, FMZ last modified 2024-01-25 11:49:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 158-373), RSI 9 of close; pivots left 1, right 3; range 5 to 60; take profit at RSI 80; bull, hidden bull and bear on, hidden bear off; trailing stop NONE; pyramiding 2, fixed 2
    bullCond = priceLL and oscHL and plFound;  hiddenBullCond = priceHL and oscLL and plFound;  entry RSIDivLE on either
    longClose = crossover(rsi, 80) or bearCond -> close RSIDivLE (sl_type NONE)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pivots are strict on both sides and known 3 bars after the pivot (#434470); valuewhen(..., 1) is
      the previous pivot; inRange(plFound[1]) counts the bars since the last pivot before the current
      bar (5 to 60). The second pyramiding entry is an add (sizing); one position is held. The entry and
      the close act on the position held at the bar close. The date inputs feed no order. Long only.
      The fixed quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots known after the right lookback.
    2 generic: PASS, RSI pivots and price pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity and pyramiding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND366941 (4 members, best partner #432315, Jaccard 0.790); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439954_rsi9_divergence_long_tp80"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [9, 14],
    "tp_level": [80, 70],
}
DEFAULT_PARAMS = {"len": 9, "tp_level": 80, "lbl": 1, "lbr": 3, "range_lower": 5, "range_upper": 60}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _pivot(x, left, right, low):
    """True at bar i when bar i - right is a strict pivot (both sides), known at bar i."""
    m = len(x)
    out = np.zeros(m, dtype=bool)
    for i in range(left + right, m):
        p = i - right
        v = x[p]
        if np.isnan(v):
            continue
        w = np.concatenate((x[p - left:p], x[p + 1:i + 1]))
        if np.isnan(w).any():
            continue
        out[i] = (v < w).all() if low else (v > w).all()
    return out


def _div(found, osc_r, px_r, lo_side, rl, ru, hidden):
    """Regular (and optionally hidden) divergence flags at pivot bars against the previous pivot."""
    m = len(found)
    out = np.zeros(m, dtype=bool)
    last_i, po, pp = -1, np.nan, np.nan
    for i in range(m):
        if found[i]:
            if last_i >= 0:
                bars = i - 1 - last_i                    # barssince(found[1]) at bar i
                ok = rl <= bars <= ru
                if lo_side:
                    reg = ok and osc_r[i] > po and px_r[i] < pp
                    hid = ok and osc_r[i] < po and px_r[i] > pp
                else:
                    reg = ok and osc_r[i] < po and px_r[i] > pp
                    hid = ok and osc_r[i] > po and px_r[i] < pp
                out[i] = reg or (hidden and hid)
            last_i, po, pp = i, osc_r[i], px_r[i]
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    osc = _rsi(c, int(p["len"]))
    L, R = int(p["lbl"]), int(p["lbr"])
    ov = osc.to_numpy()
    pl, ph = _pivot(ov, L, R, True), _pivot(ov, L, R, False)
    o_r = osc.shift(R).to_numpy()
    rl, ru = int(p["range_lower"]), int(p["range_upper"])
    bull = _div(pl, o_r, bars_df["low"].shift(R).to_numpy(), True, rl, ru, True)
    bear = _div(ph, o_r, bars_df["high"].shift(R).to_numpy(), False, rl, ru, False)
    tp = float(p["tp_level"])
    xo = ((osc > tp) & (osc.shift(1) <= tp)).to_numpy()
    close_ = xo | bear
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1:
            if close_[i]:
                lx[i], pos = True, 0
        elif bull[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
