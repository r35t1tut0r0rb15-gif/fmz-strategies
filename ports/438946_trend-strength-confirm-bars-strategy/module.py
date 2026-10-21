"""First higher / lower close, 2-hour bars: the first close above the previous close (a run of one) goes long, the first close below it goes short; reversing.
Port of FMZ strategy #438946 "Trend Strength Confirm Bars Strategy" (Confirm Bars Strategy [TS Trader]).

FMZ source id: 438946

Source
    https://www.fmz.com/strategy/438946 (PineScript v5, FMZ last modified 2024-01-16 15:22:53).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 115-139), confirm bars 1; date range true
    bcount := close[1] < close ? bcount[1] + 1 : 0;  bcount == 1 -> entry Buy;  scount := close[1] > close ? scount[1] + 1 : 0;  scount == 1 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry fires when the run of higher (lower) closes reaches exactly confirmBars. inBacktestRange is
      true. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest
      header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close runs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438946 (2 members, best partner #439064, Jaccard 0.651); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438946_confirm_bars_runs"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "confirm_bars": [1, 2, 3, 4],
}
DEFAULT_PARAMS = {"confirm_bars": 1}


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
    cv = bars_df["close"].to_numpy(dtype=float)
    m = len(cv)
    b, s = np.zeros(m), np.zeros(m)
    for i in range(1, m):
        b[i] = b[i - 1] + 1 if cv[i - 1] < cv[i] else 0.0
        s[i] = s[i - 1] + 1 if cv[i - 1] > cv[i] else 0.0
    k = int(p["confirm_bars"])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(b == k, index=ix), false, pd.Series(s == k, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
