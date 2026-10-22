"""Calm-range trend entries with a close on every held bar, 1-hour bars, long only: with the 30-bar variance of the range (as a share of the close, x 1e6) under 35 and SMA 5 > 15 > 30, go long; the stop
condition is always true, so each long closes at the first bar close it is held.
Port of FMZ strategy #446453 "Variance and Moving Averages Based Volatility Strategy" (Variance and Moving Averages Strategy).

FMZ source id: 446453

Source
    https://www.fmz.com/strategy/446453 (PineScript v5, FMZ last modified 2024-03-28 17:33:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-128), SMA 5 / 15 / 30; variance((high - low) / close, 30) x 1e6 < 35; take profit variance > 500; stop condition true
    variance < 35 and ma5 > ma15 and ma15 > ma30 -> entry Long;  true -> close Long;  variance > 500 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * stop_loss_condition is hard-coded true (its intended test is in a comment), so strategy.close is
      called on every bar: a long filled at the open after a signal is closed at the next open, and the
      take-profit test never matters. A signal while long is ignored (the close follows it in the same
      bar). ta.variance is the population variance. Long only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, calm-range trend entries with a one-bar hold.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446453_calm_range_sma_stack_one_bar_hold_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "var_max": [35.0, 100.0],
    "var_len": [30, 50],
}
DEFAULT_PARAMS = {"var_max": 35.0, "var_len": 30}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    var = ((h - lo) / c).rolling(int(p["var_len"])).var(ddof=0) * 1e6
    m5, m15, m30 = (c.rolling(n).mean() for n in (5, 15, 30))
    buy = ((var < float(p["var_max"])) & (m5 > m15) & (m15 > m30)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if held:
            lx[i] = True                            # the always-true close acts on a held long
        elif buy[i]:
            le[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
