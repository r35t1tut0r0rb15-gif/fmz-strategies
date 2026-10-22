"""EMA 50 / 150 crossings with an SMA 150 close stop and a re-entry, hourly bars: the up-cross goes long, the down-cross goes short; a long from the up-cross is closed by a close under the SMA 150, after which the close crossing back over the EMA 150 re-enters long; reversing.
Port of FMZ strategy #483108 "均线交叉趋势追踪策略结合SMA止损和重入场机制-EMA-Cross-Trend-Following-Strategy-with-SMA-Stop-Loss-and-Re-Entry-Mechanism" (EMA 50 and EMA 150 with SMA150 Stop-loss and Re-Entry #ganges).

FMZ source id: 483108

Source
    https://www.fmz.com/strategy/483108 (PineScript v6, FMZ last modified 2025-02-27 16:59:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-149), EMA 50 / 150; SMA 150; qty 1; commission 0.1 %, slippage 3
    crossover(ema50, ema150) -> entry "Buy Signal", flag := false;  crossunder -> entry "Sell Signal", flag := false
    long and close < sma150 -> close("Buy Signal"), flag := true
    flag and crossover(close, ema150) -> entry "Re-Buy Signal", flag := false;  flag and crossunder(ema50, ema150) -> entry "Re-Sell Signal", flag := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * Followed in a loop with the id of the long held: the SMA stop closes only "Buy Signal" (as written,
      strategy.close names that id), so a long opened by "Re-Buy Signal" is not closed by it, while the
      flag is set either way. A re-buy while a long is held (or its close is pending) adds nothing
      (default pyramiding refuses another id). A short has no stop; each entry on the other side reverses
      (REVERSAL INTENDED). The fixed quantity 1 is sizing; commission and slippage are costs (the house
      cost model applies). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based SMA stop.
    2 generic: PASS, EMA crossings with an SMA stop and a re-entry.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored, not ported.
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

NAME = "fmz_483108_ema50_150_cross_sma150_close_stop_reentry_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [150, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 150}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    sma = c.rolling(int(p["slow"])).mean()
    xu = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    xd = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    pu = ((c > s) & (c.shift(1) <= s.shift(1))).to_numpy()
    below = (c < sma).to_numpy()
    m = len(xu)
    le, lx, se = (np.zeros(m, dtype=bool) for _ in range(3))
    pos, lid, pend, pend_id = 0, None, None, None
    flag = False
    for i in range(m):
        if pend is not None:
            pos, lid, pend, pend_id = pend, (pend_id if pend > 0 else None), None, None
        if xu[i]:
            if pos <= 0:
                le[i], pend, pend_id = True, 1, "B"
            flag = False
        if xd[i]:
            se[i], pend, pend_id = True, -1, None
            le[i] = False
            flag = False
        if pos > 0 and below[i]:
            if lid == "B" and pend is None:
                lx[i], pend = True, 0
            flag = True
        if flag:
            if pu[i]:
                if pos <= 0 and pend is None:
                    le[i], pend, pend_id = True, 1, "R"
                flag = False
            if xd[i]:
                se[i], pend, pend_id = True, -1, None
                flag = False
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx), false


def portfolio_kwargs(**params):
    return {}
