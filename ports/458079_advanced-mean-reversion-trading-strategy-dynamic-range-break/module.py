"""SMA 30 +- 2 sd band touches, 1-hour bars: a close at or under the lower band goes long, at or over the upper band goes short; a long closes when the close crosses back over the SMA, a short when it crosses under; reversing.
Port of FMZ strategy #458079 "Advanced Mean Reversion Trading Strategy Dynamic Range Breakout System Based on Standard Deviation" (Simple Mean Reversion Strategy [nn1]).

FMZ source id: 458079

Source
    https://www.fmz.com/strategy/458079 (PineScript v5, FMZ last modified 2024-07-29 17:16:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 185-217), SMA 30, sd 30 (population), 2 sd bands
    close <= lower -> entry Long;  else close >= upper -> entry Short;  crossover(close, sma) -> close Long;  crossunder(close, sma) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are called before the closes; a close acts only on a position held into the bar and
      not being reversed on that bar (#437773). Exits are bar-close tests filled at the next open.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band touches with a return to the mean.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_458079_sma30_2sd_band_touch_mean_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [30, 20],
    "k": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 30, "k": 2.0}


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
    n, k = int(p["length"]), float(p["k"])
    s = c.rolling(n).mean()
    sd = c.rolling(n).std(ddof=0)
    long_go = (c <= s - k * sd).to_numpy()
    short_go = (c >= s + k * sd).to_numpy()
    xo = ((c > s) & (c.shift(1) <= s.shift(1))).to_numpy()
    xu = ((c < s) & (c.shift(1) >= s.shift(1))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        cur = pos
        if long_go[i]:
            cur = 1
        elif short_go[i]:
            cur = -1
        if xo[i] and pos == 1 and cur == 1:
            cur = 0                              # the close acts only on a long held, not reversed
        if xu[i] and pos == -1 and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
