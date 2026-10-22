"""Smoothed vortex crossings, 1-hour bars: the smoothed VI+ (14, WMA-seeded RMA 14) crossing over the smoothed VI- with VI- falling or the smoothed VI+ rising goes long; the mirror goes short; reversing.
Port of FMZ strategy #441997 "基于V型反转指标SMA策略V-Reversal-SMA-Strategy" (SIDD-VORTEX).

FMZ source id: 441997

Source
    https://www.fmz.com/strategy/441997 (PineScript v4, FMZ last modified 2024-02-18 15:04:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-209), vortex period 14; smoothing length 14
    VIP = sum(|high - low[1]|, 14) / sum(atr(1), 14), VIM = sum(|low - high[1]|, 14) / same;  smma = na(smma[1]) ? wma(VI, 14) : (smma[1] 13 + VI) / 14
    crossover(smmaVIP, smmaVIM) and falling(VIM) -> entry Bullish1;  crossover(smmaVIM, smmaVIP) and falling(smmaVIP) -> entry Bearish1;  crossover(smmaVIP, smmaVIM) and rising(smmaVIP) -> entry Bullish2;  crossover(smmaVIM, smmaVIP) and rising(VIM) -> entry Bearish2

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default pyramiding allows one entry in a direction, so the second long (short) id is refused
      while the first is open: one long or one short at a time. rising / falling compare with the previous
      bar, on the raw VI- and the smoothed VI+ as written. atr(1) is the bar's true range. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed vortex crossings.
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

NAME = "fmz_441997_smoothed_vortex_cross_reversal"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 21],
    "smooth_len": [14, 7],
}
DEFAULT_PARAMS = {"period": 14, "smooth_len": 14}


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


def _smma(x, n):
    seed = _wma(x, n).to_numpy()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        prev = seed[i] if np.isnan(prev) else (prev * (n - 1) + v[i]) / n
        out[i] = prev
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = int(p["period"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    strv = tr.rolling(k).sum()
    vip = (h - lo.shift(1)).abs().rolling(k).sum() / strv
    vim = (lo - h.shift(1)).abs().rolling(k).sum() / strv
    n = int(p["smooth_len"])
    sp, sm = _smma(vip, n), _smma(vim, n)
    lc = (sp > sm) & (sp.shift(1) <= sm.shift(1))
    sc = (sm > sp) & (sm.shift(1) <= sp.shift(1))
    le = lc & ((vim < vim.shift(1)) | (sp > sp.shift(1)))
    se = sc & ((sp < sp.shift(1)) | (vim > vim.shift(1)))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
