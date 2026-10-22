"""Doji states, 1-hour bars: a doji (open equal to the close) closing below the close two bars back starts a short state at that close, which lasts until a bar's low reaches the target or its high the stop
distance from it; a doji closing above the close two bars back goes long for that bar only; the short state wins; flat otherwise.
Port of FMZ strategy #440100 "Reversal Candlestick Backtesting Strategy" (Doji Backtest).

FMZ source id: 440100

Source
    https://www.fmz.com/strategy/440100 (PineScript v3, FMZ last modified 2024-01-26 16:04:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-162), take profit 10, stop loss 10 (price units, "pip"); minimum body 0.5
    pospricesell := close < close[2] and |close - open| <= 0.5 and open == close ? close : previous;  possell = pospricesell > 0 ? -1 : 0;  then reset to 0 when low <= price - 10, then when high >= price + 10
    pospricebuy := close > close[2] and doji ? close : previous;  posbuy = pospricebuy > 0 ? 1 : 0;  reset as above;  both 0 -> close_all, posbuy 1 -> entry Long, possell -1 -> entry Short;  after the orders: pospricebuy := 0 when high <= price + 10, then when low >= price - 10 (the sell lines repeat the earlier resets)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closing buy resets test the opposite side (high <= price + 10, low >= price - 10): a buy price
      that survived the earlier resets always fails one of them, so the buy price is back to 0 at every
      bar's end, and a long lasts only the bar of its doji (then close_all, unless a short state is
      live). The sell resets are repeated unchanged, so the short state lasts until its range is
      reached (often on the doji bar itself). The short entry is written after the long one and wins
      (as #437773). The body test is redundant beside open == close. All as written.
    * Criterion 2: the amounts are price units; the port uses fractions of the doji close: 0.00024 / 0.00024
      are the reading (10 / 10 on BTC near 42000), 0.01 a wider value. strategy.entry reverses: REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested state.
    2 generic: ADAPT, price-unit target / stop -> fractions of the close.
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

NAME = "fmz_440100_doji_states_short_held"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp_frac": [0.00024, 0.01],
    "sl_frac": [0.00024, 0.01],
}
DEFAULT_PARAMS = {"tp_frac": 0.00024, "sl_frac": 0.00024}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    doji = o == c
    bear = (doji & (c < c.shift(2))).to_numpy()
    bull = (doji & (c > c.shift(2))).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp_frac"]), float(p["sl_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    ps = 0.0
    for i in range(m):
        if bear[i]:
            ps = cv[i]
        short_on = ps > 0
        if ps > 0 and lv[i] <= ps * (1 - tp):
            ps = 0.0
        if ps > 0 and hv[i] >= ps * (1 + sl):
            ps = 0.0
        tgt[i] = -1 if short_on else (1 if bull[i] else 0)   # the buy price never survives a bar
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
