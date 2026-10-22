"""EMA 32 of highs and of lows, hourly bars: after a close crosses over the high EMA, the first later green candle clear of it sets a level; a break of that level followed by a green candle goes long, and a close under the low EMA closes; the mirror goes short.
Port of FMZ strategy #488244 "Cross Breakout Dual EMA System Strategy" (TrophyFighter 32 EMA HL).

FMZ source id: 488244

Source
    https://www.fmz.com/strategy/488244 (PineScript v5, FMZ last modified 2025-03-26 11:14:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-248), EMA 32 of high / low; state flags (waiting, in trade); valuewhen tests
    crossover(close, emaHigh) and no trade -> waiting long, level := na
    green candle with low > emaHigh and waiting and valuewhen(cross, bar_index, 0) > valuewhen(green clear, bar_index, 1) -> level := high
    breakout[1] (high > level, waiting) and green candle and no trade -> entry Long, in long;  close < emaLow and in long -> close Long;  mirror for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * The waiting / in-trade flags, the level and the two valuewhen tests (the last cross bar against the
      previous clear candle's bar) are followed in a loop, as written; version 5 evaluates every valuewhen
      on every bar. The flags, not the position, gate the entries; an entry and a close on the same bar
      leave the position open with the flag cleared, as written. An opposite entry would reverse
      (REVERSAL INTENDED). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA-band crossings with a first-clear-candle breakout.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488244_ema32_hl_band_cross_clear_candle_breakout_reversal"
FAMILY = "ma_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [32, 20, 50],
}
DEFAULT_PARAMS = {"length": 32}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    eh = h.ewm(span=n, adjust=False).mean()
    el = lo.ewm(span=n, adjust=False).mean()
    ca = ((c > eh) & (c.shift(1) <= eh.shift(1))).to_numpy()
    cb = ((c < el) & (c.shift(1) >= el.shift(1))).to_numpy()
    ntg = ((c > o) & (lo > eh)).to_numpy()
    ntr = ((c < o) & (h < el)).to_numpy()
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    ehv, elv = eh.to_numpy(), el.to_numpy()
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    last_ca = last_cb = g_last = g_prev = r_last = r_prev = np.nan
    fgh = frl = np.nan
    w_l = w_s = in_l = in_s = False
    lbc_prev = sbc_prev = False
    for i in range(m):
        if ca[i]:
            last_ca = i
        if cb[i]:
            last_cb = i
        if ntg[i]:
            g_prev, g_last = g_last, i
        if ntr[i]:
            r_prev, r_last = r_last, i
        if ca[i] and not in_l and not in_s:
            fgh, w_l = np.nan, True
        if cb[i] and not in_l and not in_s:
            frl, w_s = np.nan, True
        if ntg[i] and w_l and last_ca > g_prev:      # na compares false
            fgh = hv[i]
        if ntr[i] and w_s and last_cb > r_prev:
            frl = lv[i]
        lbc = (not np.isnan(fgh)) and hv[i] > fgh and w_l
        sbc = (not np.isnan(frl)) and lv[i] < frl and w_s
        lcond = lbc_prev and cv[i] > ov[i] and not in_l and not in_s
        scond = sbc_prev and cv[i] < ov[i] and not in_l and not in_s
        lbc_prev, sbc_prev = lbc, sbc
        if lcond:
            w_l, in_l = False, True
        if scond:
            w_s, in_s = False, True
        lex = cv[i] < elv[i] and in_l
        if lex:
            in_l = False
        sex = cv[i] > ehv[i] and in_s
        if sex:
            in_s = False
        le[i], se[i], lx[i], sx[i] = lcond, scond, lex, sex
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx & ~le), S(se), S(sx & ~se)


def portfolio_kwargs(**params):
    return {}
