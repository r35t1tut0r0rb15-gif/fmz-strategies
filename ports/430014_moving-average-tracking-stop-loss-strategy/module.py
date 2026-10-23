"""The MOST trailing line (3.8 % around a Hull-style EMA 28 of the close, ratcheting) against its average, 4-hour bars: the average crossing over the line goes long, crossing under goes short; reversing.
Port of FMZ strategy #430014 "Moving Average Tracking Stop Loss Strategy" (MOST Multi MAs).

FMZ source id: 430014

Source
    https://www.fmz.com/strategy/430014 (PineScript v3, FMZ last modified 2023-10-24 11:21:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 183-305), source close; average "HulleMA" 28 = ema(2 ema(14) - ema(28), round(sqrt 28) = 5); 3.8 %
    mostfiyat := avg > most[1] and avg[1] > most[1] ? max(most[1], avg - 3.8 % avg) : avg < most[1] and avg[1] < most[1] ? min(most[1], avg + 3.8 % avg) : avg > most[1] ? avg - stop : avg + stop  (most[1] via nz)
    avg > most and avg[1] < most[1] -> entry AL-Long;  avg < most and avg[1] > most[1] -> entry SAT-Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default average is the exponential Hull ("HulleMA"), lengths 28 / 2 = 14 and round(sqrt(28)) = 5;
      the other menu choices (VWMA, EVWMA among them) are not selected, so volume does not reach the orders:
      ported as not using volume (check 8). The line starts from nz = 0. REVERSAL INTENDED. The 100 % of
      equity size is sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MOST trailing line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, pyramiding 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the 2017 .. 2019 inputs are not used by the orders).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430014_most_ehma28_pct38_line_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "yuzde": [3.8, 2.0],
    "length": [28, 14],
}
DEFAULT_PARAMS = {"yuzde": 3.8, "length": 28}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    e = lambda x, k: x.ewm(span=k, adjust=False).mean()
    avg = e(2 * e(c, n // 2) - e(c, n), int(round(np.sqrt(n))))
    k = float(p["yuzde"]) / 100
    a = avg.to_numpy(dtype=float)
    m = len(a)
    most = np.zeros(m)
    prev = 0.0
    for i in range(m):
        a1 = a[i - 1] if i else np.nan
        st = a[i] * k
        if a[i] > prev and a1 > prev:
            x = max(prev, a[i] - st)
        elif a[i] < prev and a1 < prev:
            x = min(prev, a[i] + st)
        else:
            x = a[i] - st if a[i] > prev else a[i] + st
        most[i] = x
        prev = 0.0 if np.isnan(x) else x
    ms = pd.Series(most, index=c.index)
    le = (avg > ms) & (avg.shift(1) < ms.shift(1))
    se = (avg < ms) & (avg.shift(1) > ms.shift(1))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
