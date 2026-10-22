"""Bollinger (51, 1.1) band pokes and returns with named entries, 1-hour bars: a high above the upper band buys ("Buy", closed once a low is back under the upper band), a low under the lower band sells
("Sell", closed once a high is back over it); a close falling back inside from above the upper band (above the basis) opens "Long", the mirror "Short"; reversing.
Port of FMZ strategy #442342 "Bollinger Bands Breakout Trading Strategy" (FFFDBTC).

FMZ source id: 442342

Source
    https://www.fmz.com/strategy/442342 (PineScript v5, FMZ last modified 2024-02-21 11:35:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-167), BB 51 x 1.1; dates 1972-9999 (window() true); 100 % of equity, capital 100, commission 0.15 %
    high > upper -> entry Buy;  low < upper and long -> close Buy;  low < lower -> entry Sell;  high > lower and short -> close Sell
    close[1] > upper[1] and close < upper and close > basis -> entry Long;  close[1] < lower[1] and close > lower and close < basis -> entry Short
    exit("Exit_Long", "Long", stop = sma(close, 51), when = close >= basis);  exit("Exit_Short", "Short", stop = sma, when = close <= basis)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported in call order with one position at a time (default pyramiding): an entry in the held
      direction under another id does nothing, each close names its own id and acts only on the held
      position, and a close written after a reversing entry leaves the reversal standing (as #438020). The
      stops for "Long" / "Short" are re-sent at the current basis on every qualifying bar, a moving level
      the house stops (fixed at the fill) cannot express: kept pending (mark trailing_stop_pending, as
      #437036). Pine's stdev is the population deviation. REVERSAL INTENDED. The 100 % of equity size,
      capital and commission are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, band pokes and returns; the basis stops are pending.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442342_bb_poke_return_named_entries_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [51, 20],
    "mult": [1.1, 2.0],
}
DEFAULT_PARAMS = {"length": 51, "mult": 1.1}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    e_buy = (h > up).to_numpy()
    x_buy = (lo < up).to_numpy()
    e_sell = (lo < dn).to_numpy()
    x_sell = (h > dn).to_numpy()
    e_long = ((c.shift(1) > up.shift(1)) & (c < up) & (c > basis)).to_numpy()
    e_short = ((c.shift(1) < dn.shift(1)) & (c > dn) & (c < basis)).to_numpy()
    side = {None: 0, "Buy": 1, "Long": 1, "Sell": -1, "Short": -1}
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = None
    for i in range(m):
        new = held
        if e_buy[i] and side[new] != 1:
            new = "Buy"
        if x_buy[i] and held == "Buy" and new == "Buy":
            new = None
        if e_sell[i] and side[new] != -1:
            new = "Sell"
        if x_sell[i] and held == "Sell" and new == "Sell":
            new = None
        if e_long[i] and side[new] != 1:
            new = "Long"
        if e_short[i] and side[new] != -1:
            new = "Short"
        tgt[i] = side[new]
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
