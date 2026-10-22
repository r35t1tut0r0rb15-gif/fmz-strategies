"""EMA 50 side with the undisplaced cloud colour, 1-hour bars: the close above the EMA 50 with span A above span B goes long, the close under it with span B above A short; a long also closes when the
close falls under the EMA 50; reversing.
Port of FMZ strategy #442275 "Quantitative Trading Strategy Based on Ichimoku Cloud and Moving Average" (Ichimoku Cloud + ema 50 Strategy).

FMZ source id: 442275

Source
    https://www.fmz.com/strategy/442275 (PineScript v5, FMZ last modified 2024-02-20 17:12:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-180), EMA 50; Ichimoku 9 / 26 / 52, displacement 1 (plots)
    buy = close > ema50 and leadLine1 > leadLine2 -> entry Buy;  sell = close < ema50 and leadLine2 > leadLine1 -> entry Sell
    opentrades > 0 and close < ema50 -> close Buy;  opentrades < 0 and close > ema50 -> close Sell (never: opentrades is a count)

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.opentrades counts open trades and is never negative, so the short's close never fires;
      shorts end at the next long entry. A close acts only on the held position; the close written after
      a reversing entry leaves the reversal standing (as #438020). The conditions are levels. REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA side and cloud colour.
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

NAME = "fmz_442275_ema50_side_cloud_colour_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [50, 100],
    "base": [26, 52],
}
DEFAULT_PARAMS = {"len": 50, "base": 26, "conv": 9, "span2": 52}


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

    def don(k):
        return (lo.rolling(k).min() + h.rolling(k).max()) / 2

    l1 = (don(int(p["conv"])) + don(int(p["base"]))) / 2
    l2 = don(int(p["span2"]))
    e = c.ewm(span=int(p["len"]), adjust=False).mean()
    el = ((c > e) & (l1 > l2)).to_numpy()
    es = ((c < e) & (l2 > l1)).to_numpy()
    xl = (c < e).to_numpy()
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
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    false = pd.Series(False, index=ix)
    return le, lx, se, false


def portfolio_kwargs(**params):
    return {}
