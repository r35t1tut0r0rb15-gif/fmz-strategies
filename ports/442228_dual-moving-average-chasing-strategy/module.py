"""Heikin-Ashi flips, 1-hour bars: an HA close crossing over the HA open on a flat-bottomed green candle goes long, the mirror on a flat-topped red candle short; the next HA open / close cross closes it;
reversing.
Port of FMZ strategy #442228 "Dual Moving Average Chasing Strategy" (平均K腳本交易策略).

FMZ source id: 442228

Source
    https://www.fmz.com/strategy/442228 (PineScript v4, FMZ last modified 2024-02-20 14:11:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-170), Heikin Ashi from security("60") on a 1-hour chart (the chart's own bars); add-on counters unused
    long = crossover(haClose, haOpen) and green and haLow == haOpen -> entry Buy;  short = crossunder(haClose, haOpen) and not green and haHigh == haOpen -> entry Sell
    crossover(haOpen, haClose) or crossunder(haOpen, haClose) -> close Buy, close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "60" security on a 1-hour chart is the chart's own bars; Heikin Ashi is built from them. The
      exit cross also fires on every entry bar; a close acts only on the held position, so the entry
      stands, and a close written after a reversing entry leaves the reversal standing (as #438020). The
      next HA cross closes. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Heikin-Ashi crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442228_heikin_ashi_flat_flip_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {}
DEFAULT_PARAMS = {}


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
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(cv)
    hac = (ov + hv + lv + cv) / 4
    hao = np.empty(m)
    for i in range(m):
        hao[i] = (ov[i] + cv[i]) / 2 if i == 0 else (hao[i - 1] + hac[i - 1]) / 2
    hah = np.maximum(hv, np.maximum(hao, hac))
    hal = np.minimum(lv, np.minimum(hao, hac))
    hc, ho = pd.Series(hac, index=bars_df.index), pd.Series(hao, index=bars_df.index)
    xo = ((hc > ho) & (hc.shift(1) <= ho.shift(1))).to_numpy()
    xu = ((hc < ho) & (hc.shift(1) >= ho.shift(1))).to_numpy()
    el = xo & (hao < hac) & (hal == hao)
    es = xu & ~(hao < hac) & (hah == hao)
    ex = xo | xu
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if es[i] and new != -1:
            new = -1
        if ex[i] and held == 1 and new == 1:
            new = 0
        if ex[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
