"""Cloud, EMA 20 and MACD confluence, 1-hour bars, long only: with a bullish or cleared cloud (spans of 25 bars ago), the
close above the EMA 20 and a positive MACD histogram the strategy goes long; the bearish mirror closes it.
Port of FMZ strategy #434159 "The Great Delight Multifactor Quantitative Strategy" (MACD/EMA/SMA/Ichimoku Long Strategy).

FMZ source id: 434159

Source
    https://www.fmz.com/strategy/434159 (PineScript v2, FMZ last modified 2023-12-04 13:04:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 162-225), Ichimoku 9 / 26 / 52 / 26; SMA 200; EMA 20; MACD 12 / 26 / 9
    upper = lead1[25], bottom = lead2[25];  buy = ((upper > bottom or close > max) and close > ema20 and delta > 0 and close > min) or (close < sma200 and delta > 0 and close > ema20 and (upper > bottom or close > max))
    sell = the mirror;  buy -> entry long;  sell -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "buy_entry = false" / "sell_entry = false" lines inside the if blocks declare new local
      variables (= not :=), so they change nothing: the entry and exit conditions are the first
      expressions only, as written.
    * The entry is a level (ignored while long). Long only; Opposite entries cannot occur. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cloud position, EMA and MACD sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434159_cloud_ema_macd_long"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 50],
    "conv": [9, 20],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span2": 52, "disp": 26, "sma_len": 200, "ema_len": 20}


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

    def don(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    l1 = (don(p["conv"]) + don(p["base"])) / 2
    l2 = don(p["span2"])
    k = int(p["disp"]) - 1
    up_c, bot = l1.shift(k), l2.shift(k)
    mx = pd.concat([up_c, bot], axis=1).max(axis=1, skipna=False)
    mn = pd.concat([up_c, bot], axis=1).min(axis=1, skipna=False)
    sma = c.rolling(int(p["sma_len"])).mean()
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    delta = macd - macd.ewm(span=9, adjust=False).mean()
    bull_c = (up_c > bot) | (c > mx)
    bear_c = (up_c < bot) | (c < mn)
    buy = ((bull_c & (c > ema) & (delta > 0) & (c > mn))
           | ((c < sma) & (delta > 0) & (c > ema) & bull_c)).to_numpy()
    sell = ((bear_c & (c < ema) & (delta < 0) & (c < mx))
            | ((c > sma) & (delta < 0) & (c < ema) & bear_c)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and buy[i]:
            pos = 1
        elif pos == 1 and sell[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
