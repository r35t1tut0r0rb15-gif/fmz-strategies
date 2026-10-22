"""Ichimoku-style channel crossings, 2-hour bars: a close crossing over the 51-bar mid line with the close over the displaced span 2 and span 1 over span 2 goes long, the mirror goes short; reversing. The 0.1 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #458067 "Magic-Channel-Price-Action-Trading-Strategy-魔法通道价格行为交易策略" (Magic Channel).

FMZ source id: 458067

Source
    https://www.fmz.com/strategy/458067 (PineScript v5, FMZ last modified 2024-07-29 16:53:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 231-327), mid lines (lowest low + highest high) / 2 over 5 / 51 / 68 bars; spans displaced 21 bars; stop 0.1 %, target 0.1 % of the current close
    close > lead2[21] and lead1[21] > lead2[21] and crossover(close, base) -> entry Long;  close < lead1[21] and lead1[21] < lead2[21] and crossunder(close, base) -> entry Short
    every bar while long / short: exit(stop = close x (1 -+ 0.001), limit = close x (1 +- 0.001))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The displaced spans are the spans of 21 bars ago (past values only). The bracket is re-sent on
      every bar from that bar's close, so its levels move after entry: stops() cannot express a level
      re-set every bar, so it is described here and kept pending (as #438034, mark
      trailing_stop_pending). Positions end at the opposite entry until then. The candle and arrow
      plots are drawing only. REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header
      (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel mid-line crossings with displaced spans; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
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

NAME = "fmz_458067_magic_channel_base_cross_displaced_spans_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [5, 9],
    "base": [51, 26],
    "displace": [21, 26],
}
DEFAULT_PARAMS = {"conversion": 5, "base": 51, "displace": 21, "lagging": 68,
                  "sl_pct": 0.001, "tp_pct": 0.001}


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
