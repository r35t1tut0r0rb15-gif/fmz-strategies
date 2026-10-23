"""The ratio of the 14-bar volume SMA to its previous value crossing 1.5, 3-minute bars: crossing over goes long, crossing under goes short; reversing.
Port of FMZ strategy #429775 "Quantum Volume Strategy" (Quantum Volume Strategy).

FMZ source id: 429775

Source
    https://www.fmz.com/strategy/429775 (PineScript v5, FMZ last modified 2023-10-20 16:28:44).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 158-184), period 14, threshold 1.5
    qv = sma(volume, 14) / sma(volume, 14)[1];  crossover(qv, 1.5) -> entry Long and close Short;  crossunder(qv, 1.5) -> entry Short and close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each crossing both opens its side and closes the other, so it is a reversal on every crossing; the
      ratio needs the 14-bar average volume to jump by half in one bar (a single huge bar), as written.
      REVERSAL INTENDED. No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-average jump crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in sma(volume, 14) / sma(volume, 14)[1]; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429775_volume_sma_ratio_threshold_cross_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "qv_period": [14, 5],
    "qv_threshold": [1.5, 1.2],
}
DEFAULT_PARAMS = {"qv_period": 14, "qv_threshold": 1.5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    v = bars_df["volume"]
    s = v.rolling(int(p["qv_period"])).mean()
    qv = s / s.shift(1).where(s.shift(1) != 0)
    th = float(p["qv_threshold"])
    le = (qv > th) & (qv.shift(1) <= th)
    se = (qv < th) & (qv.shift(1) >= th)
    false = pd.Series(False, index=v.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
