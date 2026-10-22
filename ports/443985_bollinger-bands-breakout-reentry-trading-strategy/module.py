"""Band re-entries after a break, 1-hour bars: a close back inside the bands (20, 1.7) after a close under the lower band goes long, after a close over the upper band short; the close crossing the basis
against the position closes; reversing.
Port of FMZ strategy #443985 "Bollinger Bands Breakout Reentry Trading Strategy" (Bollinger Bands (BB re-entry)).

FMZ source id: 443985

Source
    https://www.fmz.com/strategy/443985 (PineScript v5, FMZ last modified 2024-03-08 14:08:53).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 108-167), SMA 20; deviation 1.7
    sell = (close > upper)[1] and inside -> entry Sell;  buy = (close < lower)[1] and inside -> entry Buy
    long and close > basis -> close Buy;  short and close < basis -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The peak tracker is unused. The closes act on the position held at the bar. Pine's
      stdev is the population deviation. Ported in call order with one position at a time.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entries with basis exits.
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

NAME = "fmz_443985_band_break_reentry_basis_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [1.7, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.7}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    inside = (c > dn) & (c < up)
    sell = ((c > up).shift(1, fill_value=False) & inside).to_numpy()
    buy = ((c < dn).shift(1, fill_value=False) & inside).to_numpy()
    xl = (c > basis).to_numpy()
    xs = (c < basis).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if held == 1 and xl[i] and new == 1:
            new = 0
        if held == -1 and xs[i] and new == -1:
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
