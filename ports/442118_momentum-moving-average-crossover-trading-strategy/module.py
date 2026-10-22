"""MACD histogram and signal-line side, 1-hour bars: the histogram and signal both above zero goes long; the close under the EMA 5 with both below zero goes short; a long closes when the histogram turns
negative, a short when it turns positive; reversing.
Port of FMZ strategy #442118 "Momentum Moving Average Crossover Trading Strategy" (Jim's MACD).

FMZ source id: 442118

Source
    https://www.fmz.com/strategy/442118 (PineScript v2, FMZ last modified 2024-02-19 14:53:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-136), MACD 12 / 26 / 9; EMA 5; "tendies" input unused
    (close > ema5 and cross(macd, signal) and hist > 0.4 and signal > 0) or (hist > 0 and signal > 0) -> entry BUY
    (close < ema5 and cross and hist < -0.4 and signal < 0) or (close < ema5 and hist < 0 and signal < 0) -> entry SELL;  hist < 0 -> close BUY;  hist > 0 -> close SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each entry's first alternative implies its second (and binds tighter than or), so the entries reduce
      to hist > 0 and signal > 0 (long) and close < ema5 and hist < 0 and signal < 0 (short); the 0.4
      thresholds therefore never matter. A close acts only on the held position; the close written after
      a reversing entry leaves the reversal standing (as #438020). REVERSAL INTENDED. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD histogram and signal side.
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

NAME = "fmz_442118_macd_hist_signal_side_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [12, 8],
    "slow": [26, 21],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9, "ema_len": 5}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    hist = macd - sig
    ma = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    el = ((hist > 0) & (sig > 0)).to_numpy()
    es = ((c < ma) & (hist < 0) & (sig < 0)).to_numpy()
    xl, xs = (hist < 0).to_numpy(), (hist > 0).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if xs[i] and held == -1 and new == -1:
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
