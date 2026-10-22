"""Close against WMA 25 / EMA 50 / EMA 100, 1-hour bars: the close above all three goes long, below all three short; a long closes when the close is under the WMA but not under all three (mirrored for a
short); reversing.
Port of FMZ strategy #442085 "多时间轴MACD指标交叉交易策略Multi-timeframe-MACD-Indicator-Crossover-Trading-Strategy" (TC - MACDoscillator v2).

FMZ source id: 442085

Source
    https://www.fmz.com/strategy/442085 (PineScript v2, FMZ last modified 2024-02-19 11:03:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-227), WMA 25, EMA 50, EMA 100; the alternate-security and inverse options are commented out
    BTO = close > wma25 and close > ema50 and close > ema100 -> entry BTO;  STO = all three below -> entry STO
    close("BTO", close < wma25 and not STO);  close("STO", close > wma25 and not BTO)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are levels; an entry while already in that direction does nothing. A close acts
      only on the held position. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against three averages.
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

NAME = "fmz_442085_close_vs_wma25_ema50_ema100_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "wma_length": [25, 50],
    "ema2_length": [100, 200],
}
DEFAULT_PARAMS = {"wma_length": 25, "ema2_length": 100, "ema1_length": 50}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    w = _wma(c, int(p["wma_length"]))
    e1 = c.ewm(span=int(p["ema1_length"]), adjust=False).mean()
    e2 = c.ewm(span=int(p["ema2_length"]), adjust=False).mean()
    bto = ((c > w) & (c > e1) & (c > e2)).to_numpy()
    sto = ((c < w) & (c < e1) & (c < e2)).to_numpy()
    xb = ((c < w).to_numpy()) & ~sto
    xs = ((c > w).to_numpy()) & ~bto
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if bto[i] and new != 1:
            new = 1
        if sto[i] and new != -1:
            new = -1
        if xb[i] and held == 1 and new == 1:
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
