"""Breaks of the latest band-outside bar's extreme, 4-hour bars: the high above the high of the latest bar that closed under the lower band (EMA 20 +- 1.5 deviations) goes long, the low under the low of
the latest bar that closed over the upper band goes short; the bracket re-sent while a signal holds is kept pending; reversing.
Port of FMZ strategy #442979 "Bollinger Bands Breakout Trend Trading Strategy" (Bollinger Band Strategy with Early Signal (v5)).

FMZ source id: 442979

Source
    https://www.fmz.com/strategy/442979 (PineScript v5, FMZ last modified 2024-02-27 18:00:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-217), EMA 20, deviation 1.5; risk-reward 3; stop 5 % of the bar range beyond it
    close[2] > upper[2] -> upLow = low[2];  close[2] < lower[2] -> lowHigh = high[2] (kept until replaced);  high > lowHigh -> entry Buy, exit(stop = low - 0.05 range, limit = close + 3 x risk)
    low < upLow -> entry Sell, exit(stop = high + 0.05 range, limit = close - 3 x risk)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two reference levels are kept until a newer outside bar replaces them, so a signal can hold
      for many bars; the bracket is re-sent on every such bar from that bar's range and close, a moving
      level: kept pending (mark trailing_stop_pending, as #442117); positions end at the opposite entry
      until then. When both hold on one bar the later Sell wins (as #437773). Pine's stdev is the
      population deviation. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, breaks of band-outside bar extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG442979 (2 members, best partner #443101, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442979_band_outside_bar_extreme_break_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 1.5}


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
    n = int(p["length"])
    basis = c.ewm(span=n, adjust=False).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    above = (c.shift(2) > (basis + dev).shift(2)).to_numpy()
    below = (c.shift(2) < (basis - dev).shift(2)).to_numpy()
    h2, l2 = h.shift(2).to_numpy(), lo.shift(2).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    up_low = lo_high = np.nan
    for i in range(m):
        if above[i]:
            up_low = l2[i]
        if below[i]:
            lo_high = h2[i]
        lg = (not np.isnan(lo_high)) and hv[i] > lo_high
        sh = (not np.isnan(up_low)) and lv[i] < up_low
        se[i] = sh
        le[i] = lg and not sh
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
