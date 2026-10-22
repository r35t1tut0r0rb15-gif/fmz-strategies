"""SMA 15 / 30 trend state, 1-hour bars: the SMA 15 above the SMA 30 holds long, below holds short (the bar-colour filter is off); reversing on each change.
Port of FMZ strategy #442624 "Trend Following Strategy Based on Moving Average Crossover" (Noro's MAs Cross Tests v1.0).

FMZ source id: 442624

Source
    https://www.fmz.com/strategy/442624 (PineScript v2, FMZ last modified 2024-02-23 12:21:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-211), fast SMA 15, slow SMA 30 (type 1 = SMA for both); colour filter off; long and short on; 100 % of equity
    trend = ma2 > ma1 ? 1 : ma2 < ma1 ? -1 : trend[1];  up = trend == 1 and (... or col == false) -> entry Long;  dn = trend == -1 and (... or col == false) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both MA types default to 1 (SMA), so the DEMA, TEMA, KAMA and channel lines are unused. With the
      colour filter off the entries are the trend level itself, re-sent each bar and refused while held.
      strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity size is sizing. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA trend state.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_442624_noro_sma15_30_trend_state_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [15, 9],
    "slow": [30, 50],
}
DEFAULT_PARAMS = {"fast": 15, "slow": 30}


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
    upv, dnv = (f > s).to_numpy(), (f < s).to_numpy()
    m = len(c)
    trend = np.zeros(m, dtype=np.int8)
    t = 0
    for i in range(m):
        if upv[i]:
            t = 1
        elif dnv[i]:
            t = -1
        trend[i] = t
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(trend == 1, index=ix), false, pd.Series(trend == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
