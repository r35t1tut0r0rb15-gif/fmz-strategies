"""Momentum-adjusted EMA crossings and Bollinger wick buys, 1-hour bars, long only: from flat, the fast MAEMA (80, of highs) crossing over the slow MAEMA (144, of closes) with hlc3 under the upper inner band
buys and the cross back closes it; or a low at or under the 3-sigma lower band (80) buys and a high above the fast MAEMA closes it.
Port of FMZ strategy #438468 "Dynamic Momentum Weighted Moving Average Crossover Strategy" (MTSPMAC + MBHB Strategy).

FMZ source id: 438468

Source
    https://www.fmz.com/strategy/438468 (PineScript v4, FMZ last modified 2024-01-12 12:04:55).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 145-340), fast MAEMA 80 on high, slow MAEMA 144 on close; shifts 0; Bollinger 80 on close (SMA basis), base 1, increment 1, breakout 3
    MAEMA(src, n) = ema(src + (mom + change(mom, round(n / phi)) x 0.5) x sum(change(src) > 0, round(n / phi^2)) / (n / phi^2), n), mom = change(src, round(n / phi))
    up = crossover(ma1, ma2);  down = crossover(ma2, ma1);  up and hlc3 < basis + dev -> entry long;  down -> close long
    low <= basis - 3 dev -> entry longwickdown;  high > ma1 -> close longwickdown

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both entries are long under the default pyramiding (one position): an entry is taken only from
      flat, the "long" setup first when both hold, and each close acts only on its own entry while that
      trade is open at the bar close. The prediction tails, bands and labels only plot. stdev is the
      population deviation. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum-adjusted EMAs and Bollinger bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438468_maema_cross_bb_wick_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [80, 40],
    "len2": [144, 89],
}
DEFAULT_PARAMS = {"len1": 80, "len2": 144, "bb_length": 80, "bb_mult": 1.0, "break_mult": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pine_round(x):
    return int(np.floor(x + 0.5))


def _maema(src, n):
    phi = (1 + np.sqrt(5)) / 2
    ml = _pine_round(n / phi)
    pl = n / phi / phi
    mom = src - src.shift(ml)
    ups = (src.diff() > 0).astype(float).rolling(_pine_round(pl)).sum()
    x = src + (mom + (mom - mom.shift(ml)) * 0.5) * ups / pl
    return x.ewm(span=n, adjust=False).mean()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma1 = _maema(h, int(p["len1"]))
    ma2 = _maema(c, int(p["len2"]))
    k = int(p["bb_length"])
    basis = c.rolling(k).mean()
    dev = c.rolling(k).std(ddof=0)
    inner_high = basis + float(p["bb_mult"]) * dev
    break_low = basis - float(p["break_mult"]) * dev
    up = (ma1 > ma2) & (ma1.shift(1) <= ma2.shift(1))
    down = (ma2 > ma1) & (ma2.shift(1) <= ma1.shift(1))
    lc = (up & ((h + lo + c) / 3 < inner_high)).to_numpy()
    dn = down.to_numpy()
    wb = (lo <= break_low).to_numpy()
    wx = (h > ma1).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cur = 0                                              # 0 flat, 1 "long", 2 "longwickdown"
    for i in range(m):
        if cur == 1 and dn[i]:
            lx[i], cur = True, 0
        elif cur == 2 and wx[i]:
            lx[i], cur = True, 0
        elif cur == 0 and i + 1 < m:
            if lc[i]:
                le[i], cur = True, 1
            elif wb[i]:
                le[i], cur = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
