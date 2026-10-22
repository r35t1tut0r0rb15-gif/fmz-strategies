"""Bollinger 14 / 2 band re-entries of the previous bar, 1-hour bars: a red previous bar whose close crossed back over the lower band goes long with a 1 % target, a green previous bar whose close crossed back under the upper band goes short with a 1 % target; reversing.
Port of FMZ strategy #452360 "Dynamic Take Profit Bollinger Bands Strategy" (Future Price Prediction (dynamic take-profit Bollinger)).

FMZ source id: 452360

Source
    https://www.fmz.com/strategy/452360 (PineScript v5, FMZ last modified 2024-05-24 17:54:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-148), Bollinger 14 / 2; take profit 1 % of the signal close (no stop)
    crossover(close[1], lower[1]) and close[1] < open[1] -> entry Buy, exit(limit = close x 1.01);  crossunder(close[1], upper[1]) and close[1] > open[1] -> entry Sell, exit(limit = close x 0.99)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crossing and the bar colour are of the previous bar. The target is fixed on the signal bar
      from its close: ported as the fixed fraction 0.01 of the fill (as #437751). A repeat signal
      inside the trade re-issues the target from that bar's close, which stops() cannot express: the
      port keeps the opening level and marks trailing_stop_pending (as #434428). Both exits share the
      id 'Take Profit', so an opposite entry's call replaces it. There is no stop. REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target as a fixed fraction; re-issued targets pending (mark).
    2 generic: PASS, band re-entries with a fixed target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_452360_bollinger14_prev_bar_reentry_1pct_target_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [14, 20],
    "mult": [2.0, 2.5],
    "tp_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"length": 14, "mult": 2.0, "tp_pct": 0.01}


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
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    c1, c2, o1 = c.shift(1), c.shift(2), o.shift(1)
    le = (c1 > lower.shift(1)) & (c2 <= lower.shift(2)) & (c1 < o1)
    se = (c1 < upper.shift(1)) & (c2 >= upper.shift(2)) & (c1 > o1)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
