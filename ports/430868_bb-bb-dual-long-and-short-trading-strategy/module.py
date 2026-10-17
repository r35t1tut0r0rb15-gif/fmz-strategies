"""Bollinger band fades from flat (samuelkanneman), 2-minute bars: a close at or above the upper band (20, 2) goes short, at
or below the lower band goes long; a close 5 % in profit, 1 % against the signal close, or at the opposite band closes
the position.
Port of FMZ strategy #430868 "BB双重多空头交易策略BB-Dual-Long-and-Short-Trading-Strategy" (MI_BB).

FMZ source id: 430868

Source
    https://www.fmz.com/strategy/430868 (PineScript v5, FMZ last modified 2023-11-02 15:40:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 195-259), BB 20 / 2, TP 5 %, SL 1 %
    flat: close >= upper -> entry short, SL = close x 1.01, TP = close x 0.99 x ... (TP = close x 0.95)
    flat: close <= lower -> entry long, SL = close x 0.99, TP = close x 1.05
    short: close <= TP or close <= lower or close >= SL -> close;  long: close >= TP or close >= upper or close <= SL -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels come from the signal close and are tested on bar closes with strategy.close (market
      exits at the next open): exit signals, not stop orders. Exits are tested from the bar after
      the signal (the position held at the start of the bar). Entries only from flat.
    * stdev is the population deviation. Opposite entries cannot occur. FREQ = "2min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits.
    2 generic: PASS, Bollinger bands and percentage exits.
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

NAME = "fmz_430868_bb_fade_pct_exits"
FAMILY = "bollinger_reversion"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "take_p": [5.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "dev": 2.0, "take_p": 5.0, "stop_l": 1.0}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up = (basis + p["dev"] * sd).to_numpy()
    lo = (basis - p["dev"] * sd).to_numpy()
    cv = c.to_numpy(dtype=float)
    tp, sl = float(p["take_p"]) / 100, float(p["stop_l"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, SL, TP = 0, np.nan, np.nan
    for i in range(m):
        start = pos
        if start == 0:
            if cv[i] >= up[i]:
                pos, SL, TP = -1, cv[i] * (1 + sl), cv[i] * (1 - tp)
            elif cv[i] <= lo[i]:
                pos, SL, TP = 1, cv[i] * (1 - sl), cv[i] * (1 + tp)
        elif start == -1 and (cv[i] <= TP or cv[i] <= lo[i] or cv[i] >= SL):
            pos = 0
        elif start == 1 and (cv[i] >= TP or cv[i] >= up[i] or cv[i] <= SL):
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
