"""14-bar momentum sign runs, 2-hour bars: the first bar of a run of positive 14-bar momentum goes long, the first of a negative run goes short; reversing.
Port of FMZ strategy #439064 "Momentum Breakout Strategy" (Momentum Strategy [TS Trader]).

FMZ source id: 439064

Source
    https://www.fmz.com/strategy/439064 (PineScript v5, FMZ last modified 2024-01-17 13:58:19).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 149-179), confirm bars 1; momentum 14; date range true
    bcount := momentum > 0 ? bcount[1] + 1 : 0;  bcount == 1 -> entry Buy;  scount := momentum < 0 ? scount[1] + 1 : 0;  scount == 1 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry fires when the run reaches exactly confirmBars. inBacktestRange is true. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "2h" from the backtest header (bars on UTC
      multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, momentum sign runs.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND438946 (2 members, best partner #438946, Jaccard 0.651); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439064_momentum_sign_runs"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "momentum_length": [14, 28],
    "confirm_bars": [1, 3],
}
DEFAULT_PARAMS = {"momentum_length": 14, "confirm_bars": 1}


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
    mom = (c - c.shift(int(p["momentum_length"]))).to_numpy()
    m = len(mom)
    b, s = np.zeros(m), np.zeros(m)
    for i in range(m):
        pb = b[i - 1] if i > 0 else 0.0
        ps = s[i - 1] if i > 0 else 0.0
        b[i] = pb + 1 if mom[i] > 0 else 0.0
        s[i] = ps + 1 if mom[i] < 0 else 0.0
    k = int(p["confirm_bars"])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(b == k, index=ix), false, pd.Series(s == k, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
