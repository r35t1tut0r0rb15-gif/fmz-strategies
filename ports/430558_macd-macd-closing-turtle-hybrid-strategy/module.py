"""MACD histogram hybrid, 2-hour bars: MACD / signal crosses enter in their direction, counter entries come after the
histogram has moved against its side for 4 bars ("sculp") and re-entries after it has moved with its side for 2 bars
("re-enter"); a slowing histogram closes the position. The last entry written on a bar sets the side.
Port of FMZ strategy #430558 "MACD-收盘中位海龟混合策略MACD-Closing-Turtle-Hybrid-Strategy" (MACD (Puckapao)).

FMZ source id: 430558

Source
    https://www.fmz.com/strategy/430558 (PineScript v4, FMZ last modified 2023-10-30 12:16:20).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 242-391), MACD 12 / 26, signal SMA 9, re-enter delay 2, sculp delay 4
    hist = macd - sma(macd, 9); slowdown = hist >= 0 ? hist falling : hist not falling
    reenter = hist >= 0 ? hist rising : hist falling; sculp = hist >= 0 ? hist falling : hist rising
    counters: reenter_cnt / sculp_cnt +1 (capped at the delay) on their condition, else -1 (floor 0)
    cross_up -> entry long; cross_down -> entry short
    sculp and sculp_cnt >= 4 -> entry short if hist >= 0 else long; sculp_cnt := 0
    reenter and reenter_cnt >= 2 -> entry long if hist >= 0 else short; reenter_cnt := 0
    slowdown -> close every entry id

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out in the corpus copy: orders read as written (as #429505),
      with the default pyramiding (no adds): one net position.
    * Several entries on one bar: the last one written sets the side (each later entry reverses the
      earlier one at the same fill). The closes act on the position held at the start of the bar
      and only when the bar's entries leave it on the same side (then the bar ends flat); a fresh
      entry from flat, or a reversal, stands.
    * The 2017-2021 date inputs are unused (inDateRange = true). strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out cash order size stored in original_sizing.txt.
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

NAME = "fmz_430558_macd_hist_hybrid"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "reenter_delay": [2, 3],
    "sculp_delay": [4, 6],
}
DEFAULT_PARAMS = {"reenter_delay": 2, "sculp_delay": 4, "fast": 12, "slow": 26, "signal": 9}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    hist = (macd - sig).to_numpy()
    xu = ((macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    xd = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    rd, sd = int(p["reenter_delay"]), int(p["sculp_delay"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos, rcnt, scnt = 0, 0, 0
    for i in range(m):
        h, h1 = hist[i], (hist[i - 1] if i > 0 else np.nan)
        if np.isnan(h):
            tgt[i] = pos
            continue
        if h >= 0:
            slowdown, reenter, sculp = h1 > h, h1 < h, h1 > h
        else:
            slowdown, reenter, sculp = not (h1 > h), h1 > h, h1 < h
        rcnt = min(rcnt + 1, rd) if reenter and rcnt < rd else (rcnt if reenter else max(rcnt - 1, 0))
        scnt = min(scnt + 1, sd) if sculp and scnt < sd else (scnt if sculp else max(scnt - 1, 0))
        start, new = pos, pos
        if xu[i]:
            new = 1
        if xd[i]:
            new = -1
        if sculp and scnt >= sd:
            new = -1 if h >= 0 else 1
            scnt = 0
        if reenter and rcnt >= rd:
            new = 1 if h >= 0 else -1
            rcnt = 0
        if slowdown and start != 0 and new == start:
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
