"""SMA 13 / SMA 144 cross, long only: the fast average crossing above the slow one goes long, crossing
back under closes the long.
Port of FMZ strategy #427436 "Moving Average Crossover Strategy".

FMZ source id: 427436

Source
    https://www.fmz.com/strategy/427436 (PineScript v2, FMZ last modified 2023-09-21 10:28:27).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 218-244), fast 13, slow 144, type 1 (SMA), slow-as-factor off
    crossover(fast, slow) and window() -> entry long; crossunder(fast, slow) or time > finish -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * window() is the constant true and `time > finish` (1 January 2020) is the author's backtest
      window end: dropped (taken literally, every long after 2020 would close on its next bar).
    * `ma_type` 1 = SMA (default), 2 = EMA, as the source's "Type" input.
    * Long only; entries only from flat.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths only.
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
import pandas as pd

NAME = "fmz_427436_sma_13_144_long"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ma": [13, 21],
    "slow_ma": [144, 89],
    "ma_type": [1, 2],
}
DEFAULT_PARAMS = {"fast_ma": 13, "slow_ma": 144, "ma_type": 1}


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
    if int(p["ma_type"]) == 2:
        f = c.ewm(span=int(p["fast_ma"]), adjust=False).mean()
        s = c.ewm(span=int(p["slow_ma"]), adjust=False).mean()
    else:
        f, s = c.rolling(int(p["fast_ma"])).mean(), c.rolling(int(p["slow_ma"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).astype(bool)
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return up, dn, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
