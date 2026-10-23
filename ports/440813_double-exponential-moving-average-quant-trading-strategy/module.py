"""Two-hour bars, long only: the EMA 5 crossing over the SMA 20 with a positive and non-falling trend intensity index (30 bars against the SMA 60) goes long; a close 5 % above or below the last signal's close closes it.
Port of FMZ strategy #440813 "Double Exponential Moving Average Quant Trading Strategy" (EMA-SMA Crossover Strategy).

FMZ source id: 440813

Source
    https://www.fmz.com/strategy/440813 (PineScript v5, FMZ last modified 2024-02-02 11:41:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 169-221), EMA 5 / SMA 20; TII major 60, minor 30; exit +-5 % from the signal close
    tii = 100 x sum(max(src - sma60, 0)) / (sum(max(src - sma60, 0)) + sum(max(sma60 - src, 0))) over 30 bars;  buyCondition = crossover(ema5, sma20) and tii > 0 and tii >= tii[1]
    entryPrice := close on every buyCondition;  opentrades > 0 and |close / entryPrice - 1| >= 0.05 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The TII loop treats a missing SMA 60 as 0 (so the first 59 bars count the whole price as above).
      The reference is the close of the latest buy signal, which also resets while already long (weird
      case: a repeated signal moves the +-5 % band). The volume SMA is unused (its filter is commented
      out): volume is not used. Long only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based +-5 % exit in the signals.
    2 generic: PASS, EMA / SMA crossings filtered by the trend intensity index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440813_ema5_sma20_cross_tii_band_exit_2h_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "major": [60, 30],
    "band": [0.05, 0.03],
}
DEFAULT_PARAMS = {"major": 60, "minor": 30, "band": 0.05}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e5 = c.ewm(span=5, adjust=False).mean()
    s20 = c.rolling(20).mean()
    d = c - c.rolling(int(p["major"])).mean().fillna(0.0)
    n = int(p["minor"])
    pos_s = d.clip(lower=0).rolling(n, min_periods=1).sum()
    neg_s = (-d).clip(lower=0).rolling(n, min_periods=1).sum()
    tot = pos_s + neg_s
    tii = 100 * pos_s / tot.where(tot != 0)
    buy = ((e5 > s20) & (e5.shift(1) <= s20.shift(1)) & (tii > 0) & (tii >= tii.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    band = float(p["band"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ref = 0, np.nan
    for i in range(m):
        if buy[i]:
            ref = cv[i]
        if pos == 1 and abs(cv[i] / ref - 1) >= band:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
