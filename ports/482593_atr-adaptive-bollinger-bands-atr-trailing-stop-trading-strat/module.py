"""Bollinger band (20, 2) re-entries, hourly bars: the close crossing back over the lower band goes long, crossing back under the upper band goes short; a close crossing a ratcheting 3 ATR line (from the closes while the position is held) closes; reversing.
Port of FMZ strategy #482593 "自适应布林带ATR跟踪止损交易策略-Adaptive-Bollinger-Bands-ATR-Trailing-Stop-Trading-Strategy" (ATR Trailing Stop Loss with Bollinger Bands).

FMZ source id: 482593

Source
    https://www.fmz.com/strategy/482593 (PineScript v5, FMZ last modified 2025-02-19 11:00:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 84-159), BB 20 x 2.0; ATR 14 x 3.0 trailing line on closes
    position > 0: long_stop := max(close - 3 atr, nz(long_stop[1], long_stop)), else na;  position < 0: short_stop := min(close + 3 atr, ...), else na
    crossover(close, lower) -> entry Long;  crossunder(close, upper) -> entry Short;  crossunder(close, long_stop) -> close Long;  crossover(close, short_stop) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing lines are script values computed from closes while the position is held (na when flat,
      so no crossing on the first held bar) and their crossings are bar-close exits, not broker stops: a
      loop that keeps the position. The entries come before the closes, so a close acts only on a position
      held into the bar and not reversed on it (as #441963). REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based trailing exits in the loop.
    2 generic: PASS, band re-entries with an ATR trailing exit.
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

NAME = "fmz_482593_bb20_reentry_close_atr3_trail_line_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_multiplier": [3.0, 2.0],
    "bb_length": [20, 50],
}
DEFAULT_PARAMS = {"atr_multiplier": 3.0, "bb_length": 20, "bb_stddev": 2.0, "atr_length": 14}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    k = float(p["bb_stddev"])
    up, dn = mid + k * sd, mid - k * sd
    lc = ((c > dn) & (c.shift(1) <= dn.shift(1))).to_numpy()
    sc = ((c < up) & (c.shift(1) >= up.shift(1))).to_numpy()
    off = (_atr(bars_df, int(p["atr_length"])) * float(p["atr_multiplier"])).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    ls_prev = ss_prev = np.nan
    for i in range(m):
        if pend in (1, -1):
            pos = pend
        elif pend == 2:
            pos = 0
        pend = 0
        ls = ss = np.nan
        if pos == 1:
            ls = cv[i] - off[i]
            if not np.isnan(ls_prev):
                ls = max(ls, ls_prev)
        if pos == -1:
            ss = cv[i] + off[i]
            if not np.isnan(ss_prev):
                ss = min(ss, ss_prev)
        ex_l = i > 0 and cv[i] < ls and cv[i - 1] >= ls_prev
        ex_s = i > 0 and cv[i] > ss and cv[i - 1] <= ss_prev
        new = 0
        if lc[i] and pos != 1:
            new = 1
        if sc[i] and pos != -1:
            new = -1                              # the later call wins a bar with both entries
        if new == 1:
            le[i], pend = True, 1
        elif new == -1:
            se[i], pend = True, -1
        elif pos == 1 and ex_l:
            lx[i], pend = True, 2
        elif pos == -1 and ex_s:
            sx[i], pend = True, 2
        ls_prev, ss_prev = ls, ss
    idx = c.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
