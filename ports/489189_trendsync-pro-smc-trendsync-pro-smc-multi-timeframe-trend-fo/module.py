"""Hourly bars against the last confirmed 20 / 20 pivot, from flat: a close crossing over the last pivot low goes long (previous close up), a close crossing under the last pivot high goes short (previous close down), each with a 1 % stop and 2 % target from the signal close; a close crossing back through the pivot level closes.
Port of FMZ strategy #489189 "TrendSync-Pro-SMC-多时间框架趋势跟随策略-TrendSync-Pro-SMC-Multi-Timeframe-Trend-Following-Strategy" (TrendSync Pro (SMC)).

FMZ source id: 489189

Source
    https://www.fmz.com/strategy/489189 (PineScript v6, FMZ last modified 2025-04-02 15:42:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 181-242), pivots 20 / 20; HTF "60" (the chart); SL 1 %, TP 2 %; 1 % of equity
    pivothigh -> level := it, up := false;  pivotlow -> level := it, up := true
    flat: crossover(close, level) and close > close[1] and up -> entry Long + exit(stop = close x 0.99, limit = close x 1.02);  crossunder and close < close[1] and not up -> entry Short + mirror
    long and crossunder(close, level) -> close Long;  short and crossover -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A pivot is known at its confirmation bar, 20 bars after the extreme (strict on both sides). The
      "60" request on the hourly chart is the chart itself. The bracket is set on the signal bar and sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). Entries need a flat position at the bar's close, so a loop follows the bracket on each
      bar's high / low (as #449508) and the level-crossing closes. Opposite entries cannot occur (entries
      only from flat). Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket as fractions of the fill.
    2 generic: PASS, pivot-level crossings with a percent bracket and level exits.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 1 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489189_pivot20_level_cross_pct_bracket_level_exit_flat"
FAMILY = "pivot_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trend_period": [20, 10],
    "sl_percent": [1.0, 2.0],
}
DEFAULT_PARAMS = {"trend_period": 20, "sl_percent": 1.0}


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


def _pivot(x, side, span=5):
    """Strict pivot of x at t - span, confirmed at t (Pine ta.pivothigh / pivotlow), on rolling
    windows: the centre beats every bar of the span on each side."""
    s = x if side > 0 else -x
    centre = s.shift(span)
    left = s.shift(span + 1).rolling(span).max()
    right = s.rolling(span).max()
    return ((centre > left) & (centre > right)).to_numpy()


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    k = int(p["trend_period"])
    ph, pl = _pivot(h, 1, k), _pivot(lo, -1, k)
    hk, lk = h.shift(k).to_numpy(), lo.shift(k).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    m = len(cv)
    tv, upf = np.full(m, np.nan), np.zeros(m, dtype=bool)
    val, up = np.nan, False
    for i in range(m):
        if ph[i]:
            val, up = hk[i], False
        if pl[i]:
            val, up = lk[i], True
        tv[i], upf[i] = val, up
    q = float(p["sl_percent"]) / 100
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        xu = i >= 1 and cv[i] > tv[i] and cv[i - 1] <= tv[i - 1]
        xd = i >= 1 and cv[i] < tv[i] and cv[i - 1] >= tv[i - 1]
        if pend in (1, -1):
            pos, pend, sl, tp = pend, 0, sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend = 2
        elif pend == 2:
            pos, pend = 0, 0
        if pos == 1 and pend == 0 and (lv[i] <= sl or hv[i] >= tp):
            pos = 0                              # the bracket fills inside this bar
        elif pos == -1 and pend == 0 and (hv[i] >= sl or lv[i] <= tp):
            pos = 0
        if pos == 1 and pend == 0 and xd:
            lx[i], pend = True, 2
            continue
        if pos == -1 and pend == 0 and xu:
            sx[i], pend = True, 2
            continue
        if pos != 0 or pend != 0:
            continue
        if xu and cv[i] > cv[i - 1] and upf[i]:
            sl_n, tp_n = cv[i] * (1 - q), cv[i] * (1 + 2 * q)
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif xd and cv[i] < cv[i - 1] and not upf[i]:
            sl_n, tp_n = cv[i] * (1 + q), cv[i] * (1 - 2 * q)
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
