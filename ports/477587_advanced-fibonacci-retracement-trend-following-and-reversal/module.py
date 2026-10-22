"""Fibonacci levels of the 50-bar range, 3-hour bars: the close crossing over the 61.8 % retracement goes long, crossing under the 38.2 % retracement goes short; a close at or above the 23.6 % level closes a long, at or below the 78.6 % level closes a short; reversing.
Port of FMZ strategy #477587 "Advanced Fibonacci Retracement Trend Following and Reversal Trading Strategy" (Fibonacci Retracement Strategy for Crypto).

FMZ source id: 477587

Source
    https://www.fmz.com/strategy/477587 (PineScript v5, FMZ last modified 2025-01-06 15:43:36).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-146), lookback 50; levels 23.6 / 38.2 / 61.8 / 78.6 % down from the 50-bar high
    crossover(close, hh - 0.618 d) -> entry Long;  crossunder(close, hh - 0.382 d) -> entry Short;  close >= hh - 0.236 d -> close Long;  close <= hh - 0.786 d -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels include the current bar. A loop follows the call order: a close acts only on the held
      position (also on a bar with a same-side entry, which is ignored) and leaves a same-bar reversal
      standing; a close test from flat does nothing even when an entry is sent on that bar. On a bar with
      both entries the later short call wins (#437773). REVERSAL INTENDED. No sizing code. FREQ = "3h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Fibonacci retracement crossings with level closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477587_fib_range50_618_382_cross_level_close_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [50, 100, 20],
}
DEFAULT_PARAMS = {"lookback": 50}


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
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    d = hh - ll
    l236, l382, l618, l786 = (hh - d * k for k in (0.236, 0.382, 0.618, 0.786))
    lc = ((c > l618) & (c.shift(1) <= l618.shift(1))).to_numpy()
    sc = ((c < l382) & (c.shift(1) >= l382.shift(1))).to_numpy()
    xl = (c >= l236).to_numpy()
    xs = (c <= l786).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if lc[i] and pos != 1:
            le[i], nxt = True, 1
        if sc[i] and pos != -1:
            le[i] = False
            se[i], nxt = True, -1
        if pos == 1 and xl[i] and not se[i]:
            lx[i], nxt = True, 0
        if pos == -1 and xs[i] and not le[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
