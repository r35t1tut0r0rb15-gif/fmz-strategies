"""Range-midpoint and vortex crossings, 1-hour bars, long only: the average % distance from the 60-bar low and high crossing over zero, with the close above the high two bars back and VI+ (14) crossing over
VI-, goes long with a 10 % target and a 10 % stop; both crossing back under closes.
Port of FMZ strategy #440994 "Momentum Price Climbing Crypto Currency Strategy" (Scalper Crypto).

FMZ source id: 440994

Source
    https://www.fmz.com/strategy/440994 (PineScript v4, FMZ last modified 2024-02-04 15:38:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 163-205), candles 60; vortex 14; TP long 0.1, SL long 0.1 (fractions of the close, in ticks)
    plotg = ((close - lowest(low, 60)) / lowest(low, 60) x 100 + (close - highest(high, 60)) / highest(high, 60) x 100) / 2;  VIP = sum(|high - low[1]|, 14) / sum(atr(1), 14), VIM = sum(|low - high[1]|, 14) / same
    long = crossover(plotg, 0) and close > high[2] and crossover(VIP, VIM) -> entry long;  strategy.exit(profit = close 0.1 / mintick, loss = close 0.1 / mintick);  short = crossunder(plotg, 0) and crossunder(VIP, VIM) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is in ticks, re-sized every bar from the close: the port reads it as fixed fractions of
      the entry (as #437751), target 0.1 and stop 0.1. atr(1) is the bar's true range (the first bar's
      high - low). The short condition only closes the long. Long only. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket from the close -> fixed fractions.
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

NAME = "fmz_440994_range_mid_vortex_cross_long_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "candles": [60, 30],
    "vortex_len": [14, 28],
}
DEFAULT_PARAMS = {"candles": 60, "vortex_len": 14, "tp": 0.1, "sl": 0.1}


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
    n = int(p["candles"])
    l9, h9 = lo.rolling(n).min(), h.rolling(n).max()
    g = ((c - l9) / l9 * 100 + (c - h9) / h9 * 100) / 2
    k = int(p["vortex_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    strv = tr.rolling(k).sum()
    vip = (h - lo.shift(1)).abs().rolling(k).sum() / strv
    vim = (lo - h.shift(1)).abs().rolling(k).sum() / strv
    lsig = ((g > 0) & (g.shift(1) <= 0) & (c > h.shift(2))
            & (vip > vim) & (vip.shift(1) <= vim.shift(1))).to_numpy()
    xsig = ((g < 0) & (g.shift(1) >= 0) & (vip < vim) & (vip.shift(1) >= vim.shift(1))).to_numpy()
    s_, t_ = float(p["sl"]), float(p["tp"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 1 and i >= entry_i and xsig[i]:
            lx[i], pos = True, 0
        elif pos == 0 and lsig[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
