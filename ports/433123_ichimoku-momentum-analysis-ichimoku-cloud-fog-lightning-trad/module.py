"""Ichimoku tenkan / kijun crosses against the displaced cloud, 1-hour bars: a tenkan cross above the kijun with the close
above both spans of 26 bars ago goes long, exited by the cross back, a close under span A of 26 bars ago, a 1.5 % stop or
a 1 % target. The short mirror is entered, but its exit order uses the long-side levels (a stop below the entry), so it
closes at the next bar's open, as written.
Port of FMZ strategy #433123 "动量分析式Ichimoku云雾闪电交易策略Momentum-Analysis-Ichimoku-Cloud-Fog-Lightning-Trading-Strategy" (Ichimoku Scalping Strategy).

FMZ source id: 433123

Source
    https://www.fmz.com/strategy/433123 (PineScript v5, FMZ last modified 2023-11-24 15:49:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 129-177), tenkan 9, kijun 26, span B 52, displacement 26; SL 1.5 %, TP 1.0 %
    enterLong = crossover(tenkan, kijun) and close > spanA[26] and close > spanB[26];  exitLong = crossunder(tenkan, kijun) or close < spanA[26]
    enterShort / exitShort mirror;  position > 0 -> exit(stop = avg (1 - 1.5 %), limit = avg (1 + 1 %))
    position < 0 -> exit(stop = avg (1 - 1.5 %), limit = avg (1 + 1 %)) (the long levels, as written)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The lines are SMAs of hl2 (not Donchian mid-points), as written.
    * Longs: sl_stop 0.015 and tp_stop 0.01 of the fill. Shorts: the source's exit is a buy stop below
      the price, which triggers at once; it is placed on the fill bar's close, so the short is closed at
      the next bar's open: an exit signal on the bar after the short signal (a one-bar short). The
      house stops also apply to that short, but cannot act before its exit (vbt does not test the
      entry bar).
    * The exits act on the position held at the start of the bar, then an entry wins (a reversal is a
      strategy.entry). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent bracket.
    2 generic: PASS, Ichimoku crosses and percent exits.
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

NAME = "fmz_433123_ichimoku_scalp_bracket"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [0.015, 0.03],
    "tp_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"conv": 9, "base": 26, "span2": 52, "disp": 26, "sl_pct": 0.015, "tp_pct": 0.01}


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
    hl2 = (h + lo) / 2
    ten = hl2.rolling(int(p["conv"])).mean()
    kij = hl2.rolling(int(p["base"])).mean()
    sa = ((ten + kij) / 2).shift(int(p["disp"]))
    sb = hl2.rolling(int(p["span2"])).mean().shift(int(p["disp"]))
    up = (ten > kij) & (ten.shift(1) <= kij.shift(1))
    dn = (ten < kij) & (ten.shift(1) >= kij.shift(1))
    el = (up & (c > sa) & (c > sb)).to_numpy()
    es = (dn & (c < sa) & (c < sb)).to_numpy()
    xl = (dn | (c < sa)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if start == 1 and xl[i]:
            pos = 0
        elif start == -1:
            pos = 0          # the short's exit order (placed on its fill bar) closes it at the next open
        if el[i]:
            pos = 1
        elif es[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
