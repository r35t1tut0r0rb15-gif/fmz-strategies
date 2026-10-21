"""SMA 10 / 21 crossings, 5-minute bars: the cross up goes long, the cross down goes short; reversing. The long has a 1 % stop and a target at twice the price (unreachable); shorts end at the reversal.
Port of FMZ strategy #438048 "Dual Moving Average Crossover Strategy" (Moving Average Crossover Strategy).

FMZ source id: 438048

Source
    https://www.fmz.com/strategy/438048 (PineScript v5, FMZ last modified 2024-01-08 15:59:34).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 137-158), SMA 10 / 21; stop loss 1 (percent of the close, as ticks); profit close x 2 (as ticks)
    crossover(fast, slow) -> entry Long;  crossunder -> entry Short;  exit(from Long, loss = close x 1 / 100, profit = close x 2) (tick distances)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is written in ticks of a percent of the close; the port reads it as fixed fractions of
      the entry fill (as #437684, #437751): a 1 % stop and a 200 % target, which is never reached (as
      written). Only the long has a bracket: sl_stop / tp_stop are set on the long fills and left empty on
      the short fills. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, moving-average crossings and percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-as-ticks bracket stored.
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

NAME = "fmz_438048_sma10_21_cross_long_stop"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [10, 5],
    "stop": [0.01, 0.02],
}
DEFAULT_PARAMS = {"fast": 10, "stop": 0.01, "slow": 21, "take": 2.0}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    return up, dn


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, _ = _signals(bars_df, p)
    on_long = up.to_numpy()
    sl = pd.Series(np.where(on_long, float(p["stop"]), np.nan), index=bars_df.index)
    tp = pd.Series(np.where(on_long, float(p["take"]), np.nan), index=bars_df.index)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
