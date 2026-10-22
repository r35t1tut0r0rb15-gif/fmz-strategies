"""Ichimoku-style channel crossings, 2-hour bars: a close crossing over the 51-bar mid line with the close over the displaced span 2 and span 1 over span 2 goes long, the mirror goes short; reversing. Same rules as #458067 without its bracket (near-duplicate group, rule 7).
Port of FMZ strategy #458140 "Multi Period Dynamic Channel Crossover Strategy" (***special edition*** (Donchian channel crossings)).

FMZ source id: 458140

Source
    https://www.fmz.com/strategy/458140 (PineScript v5, FMZ last modified 2024-07-30 11:59:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 184-228), mid lines (lowest low + highest high) / 2 over 5 / 51 / 68 bars; spans displaced 21 bars
    close > lead2[21] and lead1[21] > lead2[21] and crossover(close, base) -> entry LONG;  close < lead1[21] and lead1[21] < lead2[21] and crossunder(close, base) -> entry SHORT

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rules are those of #458067 (C201) with no bracket at all; #458067's per-bar bracket is
      pending, so the two ports trade alike until it is ported. The displaced spans are the spans of 21
      bars ago (past values only). There is no exit: positions end at the opposite entry. REVERSAL
      INTENDED. No sizing code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel mid-line crossings with displaced spans.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458140_donchian_mid_base_cross_displaced_spans_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [5, 9],
    "base": [51, 26],
    "displace": [21, 26],
}
DEFAULT_PARAMS = {"conversion": 5, "base": 51, "displace": 21, "lagging": 68}


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


def _mid(h, lo, n):
    return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    conv, base = _mid(h, lo, p["conversion"]), _mid(h, lo, p["base"])
    lead1, lead2 = (conv + base) / 2, _mid(h, lo, p["lagging"])
    d = int(p["displace"])
    dl1, dl2 = lead1.shift(d), lead2.shift(d)
    le = (c > dl2) & (dl1 > dl2) & (c > base) & (c.shift(1) <= base.shift(1))
    se = (c < dl1) & (dl1 < dl2) & (c < base) & (c.shift(1) >= base.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
