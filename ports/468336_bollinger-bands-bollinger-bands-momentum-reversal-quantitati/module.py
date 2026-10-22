"""Bollinger 34 / 2 band re-entries, 45-minute bars: the close crossing back over the lower band goes long, crossing back under the upper band goes short; reversing. The stop at the current outer band is re-sent every bar and is not ported (pending).
Port of FMZ strategy #468336 "Bollinger-Bands动量反转量化策略Bollinger-Bands-Momentum-Reversal-Quantitative-Strategy" (Bollinger Bands Strategy (MBB_Strategy)).

FMZ source id: 468336

Source
    https://www.fmz.com/strategy/468336 (PineScript v5, FMZ last modified 2024-09-26 16:21:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-169), SMA 34, sd 34 (population), 2 sd bands (1 sd bands unused); stops at the current lower / upper band
    crossover(close, lower2) -> entry Buy, is_long;  crossunder(close, upper2) -> entry Sell, is_short
    is_long: exit(Buy, stop = lower2);  is_short: exit(Sell, stop = upper2)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is re-sent on every bar at that bar's band, so its level moves after entry: stops()
      cannot express a level re-set every bar, so it is described here and kept pending (as #438034,
      mark trailing_stop_pending). Positions end at the opposite entry until then. REVERSAL INTENDED. No
      sizing code. FREQ = "45min" from the backtest header (45-minute bars from midnight UTC).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entries; per-bar band stop described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_468336_bb34_band_reentry_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [34, 20],
    "multiplier": [2.0, 2.5],
}
DEFAULT_PARAMS = {"period": 34, "multiplier": 2.0}


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
    c = bars_df["close"]
    n = int(p["period"])
    mid = c.rolling(n).mean()
    dev = float(p["multiplier"]) * c.rolling(n).std(ddof=0)
    lo2, up2 = mid - dev, mid + dev
    le = (c > lo2) & (c.shift(1) <= lo2.shift(1))
    se = (c < up2) & (c.shift(1) >= up2.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
