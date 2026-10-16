"""Three inside up (HPotter), 2-hour bars, short only as written: after the bullish three-inside-up pattern the script
holds a SHORT from the pattern close until a bar's low reaches 20 price units under it or its high 20 above it (both
as ATR fractions), then closes on the next bar.
Port of FMZ strategy #430583 "Three Inside Up Reversal Strategy" (Three Inside Up Backtest).

FMZ source id: 430583

Source
    https://www.fmz.com/strategy/430583 (PineScript v3, FMZ last modified 2023-10-30 15:36:07).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 215-239), take profit 20, stop loss 20 (price units)
    pattern = open[2] > close[2] and close[1] > open[1] and close[1] <= open[2] and close[2] <= open[1] and
              close[1] - open[1] < open[2] - close[2] and close > open and close > close[1] and open > open[1] and close > open[2]
    posprice := pattern ? close : posprice[1];  pos = posprice > 0 ? -1 : 0
    pos == 0 -> close_all;  pos == -1 -> entry short
    after the orders: low <= posprice - 20 or high >= posprice + 20 -> posprice := 0 (takes effect next bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the bullish pattern opens a short (pos = -1 when posprice > 0): ported as written.
    * The level checks run after the orders, so a touch on bar t sets the flat state for bar t + 1,
      whose close_all fills at the open after it (a new pattern on bar t + 1 keeps the short).
    * Criterion 2: the 20-unit distances become tp_atr / sl_atr x Wilder ATR(14) of the pattern bar
      (20 USD is about 0.07 ATR on 2-hour BTC).
    * Short only; Opposite entries cannot occur. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-time level checks.
    2 generic: ADAPT, the price-unit distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430583_three_inside_up_short"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "dist_atr": [0.07, 0.5],
}
DEFAULT_PARAMS = {"dist_atr": 0.07}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    o1, o2, c1, c2 = o.shift(1), o.shift(2), c.shift(1), c.shift(2)
    pat = ((o2 > c2) & (c1 > o1) & (c1 <= o2) & (c2 <= o1) & ((c1 - o1) < (o2 - c2)) & (c > o) & (c > c1)
           & (o > o1) & (c > o2)).to_numpy()
    dist = (float(p["dist_atr"]) * _atr(bars_df, ATR_LEN)).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    posprice, d = 0.0, np.nan
    for i in range(m):
        if pat[i]:
            posprice, d = cv[i], dist[i]
        tgt[i] = -1 if posprice > 0 else 0
        if posprice > 0 and (lv[i] <= posprice - d or hv[i] >= posprice + d):
            posprice = 0.0
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
