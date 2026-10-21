"""Pullbacks under the EMA 9 above the EMA 75, 1-hour bars, long only: from flat, a close above the EMA 75 but under the EMA 9 buys; a close above the EMA 9 that is under the previous low closes, and so does a
close more than 10 % under the fill price.
Port of FMZ strategy #438794 "EintSimple Pullback Strategy" (Simple Pullback Strategy).

FMZ source id: 438794

Source
    https://www.fmz.com/strategy/438794 (PineScript v5, FMZ last modified 2024-01-15 14:04:54).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-194), EMA 75 / 9; stop 10 %; exit on lower close on; date filter true
    buy = close > ema 75 and close < ema 9 and flat -> entry Long;  buyPrice := open on the bar after the signal
    sell = close > ema 9 and long and close < low[1];  stop = long and (buyPrice - close) / close > 10 %;  sell or stop -> close Long, buyPrice := na

Interpretation choices (Pine rules in SURVEY_README.md)
    * buyPrice is the fill bar's open (the bar after the signal), set after the stop test of that bar, so
      the stop is tested from the bar after the fill (on the first trade buyPrice is 0 there; later na).
      All exits are close tests that fill at the next open. The entry only from flat. Long only. The 100 %
      of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested exits.
    2 generic: PASS, EMA pullback and close tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital and percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG438794 (5 members, best partner #442417, Jaccard 0.849); ND438794 (2 members, best partner #443988, Jaccard 0.717); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438794_simple_pullback_ema75_9_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1": [75, 200],
    "stop": [0.10, 0.05],
}
DEFAULT_PARAMS = {"ma1": 75, "stop": 0.10, "ma2": 9, "lower_close": True}


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
    e1 = c.ewm(span=int(p["ma1"]), adjust=False).mean().to_numpy()
    e2 = c.ewm(span=int(p["ma2"]), adjust=False).mean().to_numpy()
    ov, lv, cv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sp = float(p["stop"])
    lc_on = bool(p["lower_close"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_e, pend_x = 0, False, False
    buy_px, sig_prev = 0.0, False
    for i in range(m):
        if pend_x:                                       # orders of the last bar fill at this open
            pos, pend_x = 0, False
        if pend_e:
            pos, pend_e = 1, False
        buy = cv[i] > e1[i] and cv[i] < e2[i] and pos == 0
        sell = pos == 1 and cv[i] > e2[i] and (not lc_on or (i > 0 and cv[i] < lv[i - 1]))
        stop = pos == 1 and (buy_px - cv[i]) / cv[i] > sp
        if buy and i + 1 < m:
            le[i], pend_e = True, True
        if sig_prev:
            buy_px = ov[i]
        if sell or stop:
            lx[i], pend_x = True, True
            buy_px = np.nan
        sig_prev = buy
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
