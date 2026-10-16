"""SMA 9 / SMA 21 cross with a 1 % bracket, long only, 10-minute bars: the fast SMA crossing above the slow one goes
long with a 1 % stop and a 1 % target; crossing below closes the long.
Port of FMZ strategy #429499 "Moving Average Crossover Strategy" (Profitable Crypto Strategy).

FMZ source id: 429499

Source
    https://www.fmz.com/strategy/429499 (PineScript v5, FMZ last modified 2023-10-17 16:46:57).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 129-160), SMA 9 / 21, stop 1 %, target 1 %
    crossover(sma9, sma21) -> stop / target = close x (1 -/+ 1 %), entry long; crossunder -> close long
    exit(stop = stopLossPrice, limit = takeProfitPrice) every bar (levels kept from the signal bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are set on the signal bar from its close and kept (var): a bracket fixed at entry. The
      house sl_stop / tp_stop are 1 % of the fill (the next open): stated approximation.
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, moving-average crosses and percentages.
    3 crypto-exchange-only: no ("Crypto" in the title only; exchange pair in the header).
    4 signals only: the bracket is ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429499_sma9_21_cross_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_pct": [1.0, 2.0],
    "tp_pct": [1.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "sl_pct": 1.0, "tp_pct": 1.0}


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
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    long_e = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    long_x = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
