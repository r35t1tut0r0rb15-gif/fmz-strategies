"""1-2-3 candle patterns with an EMA 9 / 20 and MACD filter, 1-hour bars: from flat, an up / down / higher-close pattern above both EMAs with the MACD over its signal goes long, the mirror short; the next
bar against the position (a down bar for a long, an up bar for a short) closes.
Port of FMZ strategy #444003 "1-2-3-形态与-EMAMACD-和第四根蜡烛线延伸的量化交易策略1-2-3-Pattern-Quantitative-Trading-Strategy-with-EMAs-MACD-and-4th-Candle-Extension" (1-2-3 Pattern Strategy with EMAs, MACD, and 4th Candle Extension).

FMZ source id: 444003

Source
    https://www.fmz.com/strategy/444003 (PineScript v5, FMZ last modified 2024-03-08 15:03:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-139), EMA 9 / 20; MACD 12 / 26 / 9; qty 5
    long: close[3] > open[3], close[2] < open[2], close[1] > close[3], close > close[3], no open trade, close > ema9, ema20, macd > signal -> entry Buy;  close < open and open trade -> close Buy
    short mirrored -> entry Sell;  close > open and open trade -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * Entries need no open trade; each close acts only on the held id. The quantity 5 is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, three-bar pattern with trend filters; counter-bar exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444003_123_pattern_ema_macd_counter_bar_exit"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [9, 5],
    "ema_slow": [20, 50],
}
DEFAULT_PARAMS = {"ema_fast": 9, "ema_slow": 20}


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
    o, c = bars_df["open"], bars_df["close"]
    e9 = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    e20 = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    c1, c2, c3, o2, o3 = c.shift(1), c.shift(2), c.shift(3), o.shift(2), o.shift(3)
    lg = ((c3 > o3) & (c2 < o2) & (c1 > c3) & (c > c3) & (c > e9) & (c > e20) & (macd > sig)).to_numpy()
    sh = ((c3 < o3) & (c2 > o2) & (c1 < c3) & (c < c3) & (c < e9) & (c < e20) & (macd < sig)).to_numpy()
    dn, up = (c < o).to_numpy(), (c > o).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    held = 0
    for i in range(m):
        if held == 0 and lg[i]:
            le[i], held = True, 1
        elif held == 0 and sh[i]:
            se[i], held = True, -1
        elif held == 1 and dn[i]:
            lx[i], held = True, 0
        elif held == -1 and up[i]:
            sx[i], held = True, 0
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
