"""SMA 50 / SMA 200 cross, 3-minute bars: the up cross goes long (closing a short), the down cross goes short
(closing a long); the percentage take-profit and stop-loss are off by default.
Port of FMZ strategy #428856 "Moving Average Crossover Strategy" (Backtest Engine).

FMZ source id: 428856

Source
    https://www.fmz.com/strategy/428856 (PineScript v4, FMZ last modified 2023-10-10 10:44:25).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 191-290), SMA 50 / 200, TP / SL inputs 0 (off)
    longCondition = closeShort = crossover(sma50, sma200); shortCondition = closeLong = crossover(sma200, sma50)
    anti-overlap flags (entry only once per side between opposite signals) -> entry long / entry short
    exit(limit = avg x (1 + TP), stop = avg x (1 - SL)) with 0 % inputs mapped to unreachable levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default 0 % inputs the take-profit is 1000x / the stop 100 % away (and the short side's
      0 -> 1 / 1000 mapping is likewise unreachable): the exits never fill and are not ported (quoted in
      original_sizing.txt). The anti-overlap flags let every cross through, as the crosses alternate.
    * The test period (2020-05-11 plus 3650 days) is the author's backtest window: dropped.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, moving-average crosses only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the off-by-default exits stored.
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

NAME = "fmz_428856_sma50_200_cross"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    short_e = ((s > f) & (s.shift(1) <= f.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
