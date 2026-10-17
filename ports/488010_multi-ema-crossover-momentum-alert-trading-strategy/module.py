"""EMA trend entries from flat with an EMA 15 exit, a momentum-spike warning exit and a 2-bar cooldown, 3-hour bars: flat
and out of cooldown, EMA 10 above EMA 20, the close above EMA 50 and a rising EMA 5 above EMA 10 go long (shorts
mirrored); a long closes when the close falls to EMA 15 or when the EMA 5 / EMA 10 gap shrinks unusually fast.
Port of FMZ strategy #488010 "多指数均线交叉动量预警交易策略-Multi-EMA-Crossover-Momentum-Alert-Trading-Strategy" (GRIM309 CallPut Strategy).

FMZ source id: 488010

Source
    https://www.fmz.com/strategy/488010 (PineScript v6, FMZ last modified 2025-03-24 13:49:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 156-266), EMA 5 / 10 / 15 / 20 / 50, cooldown 2 bars
    openCalls = ema10 > ema20 and close > ema50 and ema5 > ema5[1] and ema5 > ema10 and flat and cooldown over
    closeCalls = long and close <= ema15 (puts mirrored with close >= ema15)
    diff_k = |ema5 - ema10| / ema10 x 100 at k bars ago; avgChange = mean |diff_k - diff_k+1|, k = 1..4
    isWarning = in a position and |diff0 - diff1| > 2.5 x avgChange and diff0 < diff1 -> close the position
    a close starts the cooldown counter at 0, + 1 at the end of each bar; entries need it >= 2 (or na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's positionState gates the entries and closes (entries only from flat), so it tracks the position;
      all closes are close-based exit signals (rule 3).
    * Opposite entries cannot occur. FREQ = "3h" from the backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and relative gaps.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_488010_ema_trend_warning_cooldown"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cooldown": [2, 4],
    "exit_len": [15, 20],
}
DEFAULT_PARAMS = {"len5": 5, "len10": 10, "exit_len": 15, "len20": 20, "len50": 50, "cooldown": 2,
                  "warn_mult": 2.5}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e5, e10, e15, e20, e50 = (c.ewm(span=int(p[k]), adjust=False).mean()
                              for k in ("len5", "len10", "exit_len", "len20", "len50"))
    up = ((e10 > e20) & (c > e50) & (e5 > e5.shift(1)) & (e5 > e10)).to_numpy()
    dn = ((e10 < e20) & (c < e50) & (e5 < e5.shift(1)) & (e5 < e10)).to_numpy()
    gap = ((e5 - e10) / e10 * 100).abs()
    d = [gap.shift(k) for k in range(6)]
    avg = sum((d[k] - d[k + 1]).abs() for k in range(1, 5)) / 4
    spike = (((d[0] - d[1]).abs() > p["warn_mult"] * avg) & (d[0] < d[1])).to_numpy()
    cv, e15v = c.to_numpy(dtype=float), e15.to_numpy(dtype=float)
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    state, since = 0, None
    for i in range(m):
        ready = since is None or since >= p["cooldown"]
        open_l = up[i] and state == 0 and ready
        open_s = dn[i] and state == 0 and ready
        close_l = state == 1 and (cv[i] <= e15v[i] or spike[i])
        close_s = state == -1 and (cv[i] >= e15v[i] or spike[i])
        if open_l:
            state, since, le[i] = 1, None, True
        if close_l:
            state, since, lx[i] = 0, 0, True
        if open_s:
            state, since, se[i] = -1, None, True
        if close_s:
            state, since, sx[i] = 0, 0, True
        if since is not None:
            since += 1
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
