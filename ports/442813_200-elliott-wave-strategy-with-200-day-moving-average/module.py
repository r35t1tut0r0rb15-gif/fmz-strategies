"""Five-bar "wave" highs and lows with an SMA 200 filter, 4-hour bars: rising highs and lows over the last five bars above the SMA 200 go long, falling ones below it go short; the opposite pattern closes;
reversing.
Port of FMZ strategy #442813 "埃利奥特波动叠加200日均线交易策略Elliott-Wave-Strategy-with-200-Day-Moving-Average" (Elliott Wave Strategy with 200 SMA).

FMZ source id: 442813

Source
    https://www.fmz.com/strategy/442813 (PineScript v4, FMZ last modified 2024-02-26 10:49:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-147), waves = high / low [1] .. [5]; SMA 200
    bullish = high[3] > high[1] and low[4] > low[2] and high[5] > high[3];  bearish = low[3] < low[1] and high[4] < high[2] and low[5] < low[3]
    bullish and close > sma200 -> entry Long;  bearish -> close Long;  bearish and close < sma200 -> entry Short;  bullish -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "waves" are the last five bars' highs and lows, as written (the comparisons point backwards in
      time). Ported in call order with one position at a time; a close after a reversing entry leaves
      the reversal standing. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lagged high / low pattern with an SMA filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442813_five_bar_wave_pattern_sma200_reversal"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [200, 100],
}
DEFAULT_PARAMS = {"sma_len": 200}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hs = {k: h.shift(k) for k in range(1, 6)}
    ls = {k: lo.shift(k) for k in range(1, 6)}
    bull = ((hs[3] > hs[1]) & (ls[4] > ls[2]) & (hs[5] > hs[3])).to_numpy()
    bear = ((ls[3] < ls[1]) & (hs[4] < hs[2]) & (ls[5] < ls[3])).to_numpy()
    sma = c.rolling(int(p["sma_len"])).mean()
    above, below = (c > sma).to_numpy(), (c < sma).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if bull[i] and above[i] and new != 1:
            new = 1
        if bear[i] and held == 1 and new == 1:
            new = 0
        if bear[i] and below[i] and new != -1:
            new = -1
        if bull[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
