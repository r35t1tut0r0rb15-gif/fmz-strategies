"""HPotter combo of the 2/20 EMA and the adaptive price zone, 1-hour bars: long while both sides say up, short while both
say down, flat otherwise. The EMA side compares a two-bar extreme on the far side of the EMA 14 with the previous close;
the APZ side is up after a low under the lower zone and down after a high above the upper zone.
Port of FMZ strategy #434183 "Double Moving Average Oscillation Trading Strategy" (Combo 2/20 EMA & Adaptive Price Zone).

FMZ source id: 434183

Source
    https://www.fmz.com/strategy/434183 (PineScript v5, FMZ last modified 2023-12-04 15:28:12).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 177-224), 2/20 EMA length 14; APZ periods 20 (EMA 5 of EMA 5), band 2; reverse false
    nXS = (min(low, low[1]) > ema14 or max(high, high[1]) < ema14) ? min(low, low[1]) : max(high, high[1]);  pema = nXS > close[1] ? -1 : nXS < close[1] ? 1 : pema[1]
    APZ: nP = ceil(sqrt(20)) = 5;  mid = ema(ema(close, 5), 5);  width = ema(ema(high - low, 5), 5);  papz = low < mid - 2 width ? 1 : high > mid + 2 width ? -1 : papz[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The APZ state has no seed (pos[1] without nz), so it is undefined until its first signal, as
      written. The band is a multiple of an averaged range, so the rule is scale-free.
    * strategy.entry reverses: REVERSAL INTENDED. reverse is false; the start date (2005) is open.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average and range-band relations.
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

NAME = "fmz_434183_combo_2_20_ema_apz"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "band_pct": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 14, "n_periods": 20, "band_pct": 2.0}


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
    xa = c.ewm(span=int(p["length"]), adjust=False).mean()
    nhh = pd.concat([h, h.shift(1)], axis=1).max(axis=1, skipna=False)
    nll = pd.concat([lo, lo.shift(1)], axis=1).min(axis=1, skipna=False)
    nxs = np.where((nll > xa) | (nhh < xa), nll, nhh)
    c1 = c.shift(1).to_numpy()
    npd = int(np.ceil(np.sqrt(int(p["n_periods"]))))
    mid = c.ewm(span=npd, adjust=False).mean().ewm(span=npd, adjust=False).mean()
    wid = (h - lo).ewm(span=npd, adjust=False).mean().ewm(span=npd, adjust=False).mean()
    bp = float(p["band_pct"])
    a_up = (lo < mid - bp * wid).to_numpy()
    a_dn = (h > mid + bp * wid).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pe, pa = 0, 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if nxs[i] > c1[i]:
                pe = -1
            elif nxs[i] < c1[i]:
                pe = 1
            if a_up[i]:
                pa = 1
            elif a_dn[i]:
                pa = -1
            tgt[i] = 1 if (pe == 1 and pa == 1) else (-1 if (pe == -1 and pa == -1) else 0)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
