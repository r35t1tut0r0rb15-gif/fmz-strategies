"""Hourly bars, long only, from flat: an open above the previous close goes long, and a close 3 % over the fill price closes.
Port of FMZ strategy #489153 "Hourly Open Close Price Differential Smart Comparison Quantitative Trading System" (1 Hour Open vs Close Buy Strategy).

FMZ source id: 489153

Source
    https://www.fmz.com/strategy/489153 (PineScript v6, FMZ last modified 2025-04-02 11:15:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 200-242), target 3 % of the average price (close-tested); 100 % of equity
    open > close[1] and flat -> entry Buy;  long and close >= avg x 1.03 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar's own open is known when its close is tested, so the signal uses it. The target is tested
      on closes against the fill price (the next bar's open) and sent as a close (an exit signal, no stop
      module); a loop follows the position, as written. Long only. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested percent target.
    2 generic: PASS, gap-up entries with a percent target.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489153_open_over_prev_close_close_target3pct_long"
FAMILY = "gap"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "target_pct": [3.0, 1.5, 6.0],
}
DEFAULT_PARAMS = {"target_pct": 3.0}


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
    o, c = bars_df["open"], bars_df["close"]
    sig = (o > c.shift(1)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    q = 1 + float(p["target_pct"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, fp = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos, fp = 1, ov[i]
        elif pend == -1:
            pos = 0
        pend = 0
        if pos == 0 and sig[i]:
            le[i], pend = True, 1
        elif pos == 1 and cv[i] >= fp * q:
            lx[i], pend = True, -1
    false = pd.Series(False, index=c.index)
    return pd.Series(le, index=c.index), pd.Series(lx, index=c.index), false, false.copy()


def portfolio_kwargs(**params):
    return {}
