"""EMA-layer dip buys with profit-gated exits, 1-minute bars, long only: a red candle closing under its previous low inside one of four EMA layers (20-50, 50-100, 100-200, under 200) buys (the layer
only sets the quantity); the long closes on a red candle under the EMA 10 (in an EMA 10 uptrend stack) once the average price is 1 % in profit and the close is under the last two lows.
Port of FMZ strategy #436137 "Mean Reversion Reverse Strategy Based on Moving Average" (EMA_zorba1).

FMZ source id: 436137

Source
    https://www.fmz.com/strategy/436137 (PineScript v5, FMZ last modified 2023-12-21 15:45:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 109-153), EMA 10 / 20 / 50 / 100 / 200; profit 1 %; quantities 5 / 10 / 15 / 20 x pyramiding 2
    buy_condition_1 = close < ema20 and close > ema50 and close < open and close < low[1];  ... _4 = close < ema200 and close < open and close < low[1]
    exit_1 = close > ema10 and ema10 > all other emas and close < open and profit and close < low[1] and close < low[2];  exit_2 = close < ema10 and close[1] > ema10 and close < close[1] and (the same stack) and red and profit and close < low[1] and close < low[2]
    profit = avg price x 1.01 <= close;  entry Buy1..Buy4 (by layer), close all four ids on exit_1 or exit_2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The four entry ids differ only by quantity (sizing); the strategy declaration sets no pyramiding,
      so one trade stands at a time and the port is a single long: enter from flat when any layer
      condition holds. The exit's average price is the entry fill (the next open). Exits are rules on
      closes filled at the next open (close-based exit signals). The date range is true (the 2021-2024
      inputs are unused). Long only. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, EMA layers and candle rules.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity inputs and the pyramiding multiplier stored.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: DG436137 (3 members, best partner #439203, Jaccard 0.948); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436137_ema_layer_dip_long_profit_exit"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "profit_pct": [1.0, 2.0, 0.5],
}
DEFAULT_PARAMS = {"profit_pct": 1.0}


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
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    e = {k: c.ewm(span=k, adjust=False).mean() for k in (10, 20, 50, 100, 200)}
    red = c < o
    dip = red & (c < lo.shift(1))
    b1 = (c < e[20]) & (c > e[50]) & dip
    b2 = (c < e[50]) & (c > e[100]) & dip
    b3 = (c < e[100]) & (c > e[200]) & dip
    b4 = (c < e[200]) & dip
    buy = (b1 | b2 | b3 | b4).fillna(False).to_numpy()
    stack = (e[10] > e[20]) & (e[10] > e[50]) & (e[10] > e[100]) & (e[10] > e[200])
    two_lows = (c < lo.shift(1)) & (c < lo.shift(2))
    x1 = ((c > e[10]) & stack & red & two_lows).fillna(False).to_numpy()
    x2 = ((c < e[10]) & (c.shift(1) > e[10].shift(1)) & (c < c.shift(1)) & stack & red & two_lows).fillna(False).to_numpy()
    ex = x1 | x2
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    gain = 1.0 + float(p["profit_pct"]) / 100.0
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg, pend = 0, np.nan, None
    for i in range(m):
        if pend == "enter":
            pos, avg = 1, ov[i]
        elif pend == "exit":
            pos, avg = 0, np.nan
        pend = None
        if pos == 0 and buy[i]:
            pend = "enter"
        elif pos == 1 and ex[i] and (avg * gain <= cv[i]):
            pend = "exit"
        tgt[i] = 1 if (pend == "enter" or (pos == 1 and pend != "exit")) else 0
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((tgt == 0) & (prev == 1), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
