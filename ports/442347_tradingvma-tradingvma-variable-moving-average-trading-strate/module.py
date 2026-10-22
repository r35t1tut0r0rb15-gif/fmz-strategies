"""Variable moving average (VMA 5) direction, 1-hour bars: the VMA rising goes long, falling goes short; reversing.
Port of FMZ strategy #442347 "可变移动平均线-TradingVMA-策略TradingVMA-Variable-Moving-Average-Trading-Strategy" (Variable Moving Average Strategy).

FMZ source id: 442347

Source
    https://www.fmz.com/strategy/442347 (PineScript v4, FMZ last modified 2024-02-21 11:47:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 164-231), VMA length 5; take profit / stop loss off; dates 2000-2019 (use_date)
    VMA = (1 - k vI) nz(VMA[1]) + k vI close, k = 1 / 5, vI = the stochastic of the smoothed directional index;  VMA > VMA[1] -> entry BUY (direction strategy.long and use_date);  VMA < VMA[1] -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * use_date is the author's bounded date window (to 2019), dropped like other date windows, so BUY is
      a long entry (as written after 2019 the "strategy.long and use_date" direction would turn the BUY
      entries short). The take-profit / stop-loss inputs are off. The VMA recursion keeps its nz starts.
      The conditions are levels; an entry while already in that direction does nothing. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VMA direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442347_variable_ma_direction_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [5, 10],
}
DEFAULT_PARAMS = {"length": 5}


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


def _vma(c, l):
    k = 1.0 / l
    v = c.to_numpy(dtype=float)
    m = len(v)
    i_s = np.full(m, np.nan)
    pdms = mdms = pdis = mdis = iS = 0.0
    for i in range(m):
        d = v[i] - v[i - 1] if i > 0 else np.nan
        pdm = max(d, 0.0) if not np.isnan(d) else np.nan
        mdm = max(-d, 0.0) if not np.isnan(d) else np.nan
        pdms = (1 - k) * pdms + k * pdm if not np.isnan(pdm) else np.nan
        mdms = (1 - k) * mdms + k * mdm if not np.isnan(mdm) else np.nan
        s = pdms + mdms
        pdi = pdms / s if s else np.nan
        mdi = mdms / s if s else np.nan
        pdis = (1 - k) * (0.0 if np.isnan(pdis) else pdis) + k * pdi
        mdis = (1 - k) * (0.0 if np.isnan(mdis) else mdis) + k * mdi
        s1 = pdis + mdis
        dd = abs(pdis - mdis)
        iS = (1 - k) * (0.0 if np.isnan(iS) else iS) + k * (dd / s1 if s1 else np.nan)
        i_s[i] = iS
        if np.isnan(pdms):
            pdms = 0.0
        if np.isnan(mdms):
            mdms = 0.0
    iss = pd.Series(i_s, index=c.index)
    hhv, llv = iss.rolling(l).max(), iss.rolling(l).min()
    vi = ((iss - llv) / (hhv - llv)).to_numpy()
    out = np.full(m, np.nan)
    vm = 0.0
    for i in range(m):
        if np.isnan(vi[i]):
            out[i], vm = np.nan, 0.0    # an undefined VMA restarts from nz(.) = 0, as written
            continue
        vm = (1 - k * vi[i]) * vm + k * vi[i] * v[i]
        out[i] = vm
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    vma = _vma(c, int(p["length"]))
    le = vma > vma.shift(1)
    se = vma < vma.shift(1)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
