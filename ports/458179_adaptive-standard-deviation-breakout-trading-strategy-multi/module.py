"""Recoveries over the lower 3 sd band of the SMA 20, 1-hour bars, long only: the close crossing back over the lower band buys; a close 1 % over the fill sells, as does a close 0.5 % under it.
Port of FMZ strategy #458179 "Adaptive Standard Deviation Breakout Trading Strategy Multi Period Optimization System Based on Dynamic Volatility" (MikEy Scali 3 STD Dev Buy Strategy with TP and SL).

FMZ source id: 458179

Source
    https://www.fmz.com/strategy/458179 (PineScript v5, FMZ last modified 2024-07-30 16:09:04).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-254), SMA 20, sd 20 (population), 3 sd bands; target 1 %, stop 0.5 % of the entry price (close tests); dates 2023-2024
    crossover(close, lower) and in date range -> entry Buy
    long and close >= entry x 1.01 -> close Buy;  long and close <= entry x 0.995 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The date window is the author's backtest range and is dropped like other date windows. The
      target and stop are bar-close tests against the trade's entry (fill) price, filled at the next
      open, followed in a loop from the fill bar; the entry price is the fill open. Long only. No sizing
      code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the exits are close tests against the fill.
    2 generic: PASS, lower-band recoveries with percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458179_sma20_3sd_lower_band_recovery_pct_close_tests_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "tp_pct": [0.01, 0.02],
    "sl_pct": [0.005, 0.01],
}
DEFAULT_PARAMS = {"length": 20, "mult": 3.0, "tp_pct": 0.01, "sl_pct": 0.005}


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
    n = int(p["length"])
    lower = c.rolling(n).mean() - float(p["mult"]) * c.rolling(n).std(ddof=0)
    buy = ((c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, sl = float(p["tp_pct"]), float(p["sl_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, entry = 0, 0, np.nan
    for i in range(m):
        if pend == 1:
            pos, entry = 1, ov[i]
        elif pend == 2:
            pos, entry = 0, np.nan
        pend = 0
        if buy[i] and pos == 0:
            le[i], pend = True, 1
        if pos == 1 and (cv[i] >= entry * (1 + tp) or cv[i] <= entry * (1 - sl)):
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
