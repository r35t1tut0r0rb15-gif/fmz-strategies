"""MACD histogram zero cross with a 5 % stop, 3-hour bars: the histogram (MACD 12 / 26 minus its EMA 12) crossing up
goes long, crossing down goes short; each position has a 5 % stop from its entry price.
Port of FMZ strategy #429494 "MACD多空平衡跟踪策略MACD-Trend-Balancing-Strategy" (MACD BF).

FMZ source id: 429494

Source
    https://www.fmz.com/strategy/429494 (PineScript v2, FMZ last modified 2023-10-17 16:15:53).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 174-222), MACD 12 / 26, signal EMA 12, stop 5 %
    long = crossover(delta, 0); short = crossunder(delta, 0); long_signal / short_signal = the first of each after the other
    entry long on long_signal, entry short on short_signal
    exit(stop = avg x (1 -/+ 5 %)) from the second bar after the entry signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The crosses alternate, so long_signal / short_signal are the crosses themselves (the first cross of
      the data counts).
    * The stop is 5 % of the average entry price (the fill): sl_stop 0.05. Stated approximation: the
      source places it from the bar after the fill bar (since_entry > 1), the house from the fill.
    * strategy.entry reverses. Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED. Stops on
      3-hour bars: mark coarse_bar_stop. FREQ = "3h" from the backtest header. The date window is dropped.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry (arming approximation stated).
    2 generic: PASS, a sign cross and a percentage.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored; the stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429494_macd_hist_cross_stop"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "macd_length": [12, 9],
    "sl_pct": [5.0, 2.5],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "macd_length": 12, "sl_pct": 5.0}


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
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    macd = e(c, p["fast"]) - e(c, p["slow"])
    delta = macd - e(macd, p["macd_length"])
    up = ((delta > 0) & (delta.shift(1) <= 0)).to_numpy()
    dn = ((delta < 0) & (delta.shift(1) >= 0)).to_numpy()
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


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
