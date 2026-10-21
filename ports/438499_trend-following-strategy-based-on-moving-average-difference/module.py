"""Hull-style EMA turns with a 17:00 UTC close, 1-hour bars: the smoothed EMA difference turning up against its one-bar-old copy goes long, turning down goes short; reversing; every position is closed on the
bar opening 17:00 UTC.
Port of FMZ strategy #438499 "Trend Following Strategy Based on Moving Average Difference" (Devick).

FMZ source id: 438499

Source
    https://www.fmz.com/strategy/438499 (PineScript v5, FMZ last modified 2024-01-12 14:42:06).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 171-215), period 21 (EMA 11 / 21, smoothing 5); close hour 17
    n1 = ema(2 ema(close, 11) - ema(close, 21), 5);  n2 = the same of close[1];  buy = n1 > n2 and n1[1] <= n2[1] -> entry Buy;  sell = n1 <= n2 and n1[1] > n2[1] -> entry Sell
    hour == 17 and minute == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour is read on the bar's UTC open time (the exchange time zone, as #435514). The close_all is
      written after the entries: it acts on the position held at the bar close, so on the 17:00 bar an
      open position is closed and an opposite entry is not taken (the bar ends flat, as #430380); from
      flat, an entry on that bar opens. Pine's round is half away from zero (21 / 2 -> 11). strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed EMA difference turns; a UTC clock close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: UTC hour 17 close.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438499_devick_turns_17utc_close"
FAMILY = "hull_ma"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [21, 34],
    "close_hour": [17, 21],
}
DEFAULT_PARAMS = {"period": 21, "close_hour": 17}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _pine_round(x):
    return int(np.floor(x + 0.5))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["period"])
    half, sq = _pine_round(n / 2), _pine_round(np.sqrt(n))

    def _n(src):
        diff = 2 * src.ewm(span=half, adjust=False).mean() - src.ewm(span=n, adjust=False).mean()
        return diff.ewm(span=sq, adjust=False).mean()

    n1, n2 = _n(c), _n(c.shift(1))
    buy = ((n1 > n2) & (n1.shift(1) <= n2.shift(1))).to_numpy()
    sell = ((n1 <= n2) & (n1.shift(1) > n2.shift(1))).to_numpy()
    ix = bars_df.index.tz_convert("UTC")
    clk = (ix.hour == int(p["close_hour"])) & (ix.minute == 0)
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if clk[i] and pos != 0:
            if pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = 0
        elif buy[i] and pos != 1 and i + 1 < m:
            le[i], pos = True, 1
        elif sell[i] and pos != -1 and i + 1 < m:
            se[i], pos = True, -1
    bi = bars_df.index
    return (pd.Series(le, index=bi), pd.Series(lx, index=bi),
            pd.Series(se, index=bi), pd.Series(sx, index=bi))


def portfolio_kwargs(**params):
    return {}
