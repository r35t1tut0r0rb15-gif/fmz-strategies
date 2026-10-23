"""The Schaff trend cycle (EMA 23 / 50 MACD, cycle 10, two EMA 3 stages) crossing its 10 / 90 lines, hourly bars: crossing over 10 goes long, crossing under 90 goes short, each with a 5 % stop and a 10 % target from the entry; reversing.
Port of FMZ strategy #430838 "Multi indicator Strategy to Identify Trading Inflection Points in Quant Trading" (WOMBO COMBO: 100/200EMA & VWAP & MACD).

FMZ source id: 430838

Source
    https://www.fmz.com/strategy/430838 (PineScript v4, FMZ last modified 2023-11-02 14:09:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 272-469), STC 23 / 50, cycle 10, D 3 / 3, limits 90 / 10; EMA / VWAP / MACD / BB filters off; SL 5 %, TP 10 %; strategy() commented out
    STCbuy = crossover(stc, 10) -> entry HC-Long;  STCsell = crossunder(stc, 90) -> entry HC-Short
    long -> exit("Close Long", stop = avg x 0.95, limit = avg x 1.1);  short -> exit("Close Short", stop = avg x 1.05, limit = avg x 0.9)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the STC test is on; the EMA, VWAP, MACD and Bollinger tests are off, so volume (VWAP) does not
      reach the orders: ported as not using volume (check 8). The exits carry no entry id and are sent for
      the open side, a 5 % / 10 % bracket of the fill (scalar fractions). The STC keeps its last value
      while a window's range is 0 (fixnan) and starts from 0 (nz). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). strategy() is commented out. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, Schaff trend cycle crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (1.5 % of equity, slippage 2) stored, not ported.
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

NAME = "fmz_430838_schaff_trend_cycle_10_90_cross_pct_bracket_reversal"
FAMILY = "oscillator_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cycle_length": [10, 20],
    "stop": [0.05, 0.03],
}
DEFAULT_PARAMS = {"cycle_length": 10, "stop": 0.05, "take": 0.10, "upper": 90.0, "lower": 10.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["cycle_length"])
    st = lambda x: 100 * (x - x.rolling(n).min()) / (x.rolling(n).max() - x.rolling(n).min()).replace(0.0, np.nan)
    macd = c.ewm(span=23, adjust=False).mean() - c.ewm(span=50, adjust=False).mean()
    k = _fixnan(st(macd)).fillna(0.0)
    d = k.ewm(span=3, adjust=False).mean()
    kd = _fixnan(st(d)).fillna(0.0)
    stc = kd.ewm(span=3, adjust=False).mean().clip(0, 100)
    lo_, up_ = float(p["lower"]), float(p["upper"])
    le = (stc > lo_) & (stc.shift(1) <= lo_)
    se = (stc < up_) & (stc.shift(1) >= up_)
    false = pd.Series(False, index=c.index)
    return le, false, se & ~le, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"]), "tp_stop": float(p["take"])}


def portfolio_kwargs(**params):
    return {}
