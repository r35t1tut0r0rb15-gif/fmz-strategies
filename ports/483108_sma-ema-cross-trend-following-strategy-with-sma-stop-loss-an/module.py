"""EMA 50 / 150 crosses with an SMA 150 close-out of the first long and re-entries, 1-hour bars: EMA 50 crossing above
EMA 150 goes long, crossing below goes short; a long opened by the cross closes on a close below SMA 150; after such a
close-out the close crossing back above EMA 150 re-buys and the next EMA cross down re-sells.
Port of FMZ strategy #483108 "均线交叉趋势追踪策略结合SMA止损和重入场机制-EMA-Cross-Trend-Following-Strategy-with-SMA-Stop-Loss-and-Re-Entry-Mechanism" (EMA 50 and EMA 150 with SMA150 Stop-loss and Re-Entry #ganges).

FMZ source id: 483108

Source
    https://www.fmz.com/strategy/483108 (PineScript v6, FMZ last modified 2025-02-27 16:59:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-144), EMA 50 / 150, SMA 150
    crossover(ema50, ema150) -> entry "Buy Signal" (long); crossunder -> entry "Sell Signal" (short); both reset the flag
    position long and close < sma150 -> close("Buy Signal"), flag = true
    flag: crossover(close, ema150) -> entry "Re-Buy Signal" (long); crossunder(ema50, ema150) -> "Re-Sell Signal"

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close("Buy Signal") closes only a long opened under that id: a long opened by "Re-Buy Signal" is not
      closed by it (it is held until the next short entry), but the flag is still set, as written.
    * One position (pyramiding default): a same-side entry while held is ignored. Closes act on the position held at
      the bar's start and never undo an entry on that bar (as #430850); a close followed by a re-buy on one bar keeps
      the long (the new trade opens at the same next open). Target-position state machine, exits only on going flat.
    * qty = 1 is sizing: not ported. Entries reverse (REVERSAL INTENDED). No stops. FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 1 quoted in original_sizing.txt and not ported.
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

NAME = "fmz_483108_ema50_150_cross_sma150_cut_reentry"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 30],
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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    sma = c.rolling(int(p["slow"])).mean()
    x_up = ((ef > es) & (ef.shift(1) <= es.shift(1))).to_numpy()
    x_dn = ((ef < es) & (ef.shift(1) >= es.shift(1))).to_numpy()
    px_up = ((c > es) & (c.shift(1) <= es.shift(1))).to_numpy()
    below = (c < sma).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, pid, flag = 0, "", False
    for i in range(m):
        start, sid = pos, pid
        if x_up[i]:
            if pos != 1:
                pos, pid = 1, "buy"
            flag = False
        if x_dn[i]:
            if pos != -1:
                pos, pid = -1, "sell"
            flag = False
        if start == 1 and below[i]:
            if sid == "buy" and pos == 1:
                pos, pid = 0, ""
            flag = True
        if flag:
            if px_up[i]:
                if pos != 1:
                    pos, pid = 1, "rebuy"
                flag = False
            if x_dn[i]:
                if pos != -1:
                    pos, pid = -1, "resell"
                flag = False
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
