"""Close vs SMA 200 side changes, hourly bars: the close moving above the SMA 200 (after being below) goes long, moving
below it (after being above) goes short.
Port of FMZ strategy #429782 "Moving Average Tracking Strategy" (MA X 200 BF).

FMZ source id: 429782

Source
    https://www.fmz.com/strategy/429782 (PineScript v4, FMZ last modified 2023-10-20 17:03:32).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 196-215), SMA 200
    long = close > sma200; short = close < sma200; long_signal / short_signal = the first bar of each after the other
    entry long on long_signal; entry short on short_signal (the exit calls have no levels: inert)

Interpretation choices (Pine rules in SURVEY_README.md)
    * last_long / last_short timestamps make the signals fire on the first bar of each side (the first
      side of the data counts). strategy.exit without levels places nothing.
    * strategy.entry reverses: REVERSAL INTENDED. The date window is dropped. FREQ = "1h" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a price-vs-average side.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429782_sma200_side_change"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [200, 100],
}
DEFAULT_PARAMS = {"length": 200}


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
    ma = c.rolling(int(p["length"])).mean()
    up, dn = (c > ma).to_numpy(), (c < ma).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = 0
    for i in range(m):
        if up[i] and last != 1:
            le[i], last = True, 1
        elif dn[i] and last != -1:
            se[i], last = True, -1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
