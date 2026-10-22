"""EMA 12 / SMA 45 crossings with a ratcheting ATR line, 3-hour bars, long only: the EMA 12 crossing over the SMA 45 goes long with a line 6 ranges under the EMA; the line rises when the EMA clears it by 6
ranges; the EMA 12 of the close falling under the line closes.
Port of FMZ strategy #441073 "Dual Moving Average Tracking Stop Loss Strategy" (XPloRR MA-Buy ATR-MA-Trailing-Stop Strategy).

FMZ source id: 441073

Source
    https://www.fmz.com/strategy/441073 (PineScript v2, FMZ last modified 2024-02-05 13:45:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-178), EMA 12, SMA 45, stop EMA 12; 6 x sma(high - low, 15); dates 2005-2050; 100 % of equity, capital 1000
    range = sma(high - low, 15);  long = crossover(ema12, sma45) and not inlong[1] -> entry buy, inlong = 1, stop = ema - 6 range
    else: stop = (ema > stop[1] + 6 range and inlong[1]) ? ema - 6 range : stop[1];  inlong = inlong[1];  stopval (ema12) < stop and inlong[1] -> close buy, inlong = 0, stop = 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line is a bar-close test of the EMA 12 of the close against a ratcheting level, sent at the next
      open (no broker stop). The state is ported as written (inlong and stop carried from the previous
      bar, nz starts). testPeriod() is always true. Long only. The 100 % of equity size and the capital are
      sizing. FREQ = "3h" from the backtest header (bars on UTC multiples of 3 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA crossings and the ratcheting line test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and capital stored.
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

NAME = "fmz_441073_ema12_sma45_cross_atr_line_long"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_period": [12, 20],
    "delta": [6, 4],
}
DEFAULT_PARAMS = {"ema_period": 12, "delta": 6, "sma_period": 45, "stop_period": 12, "range_len": 15}


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
    ema = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    sma = c.rolling(int(p["sma_period"])).mean()
    sv = c.ewm(span=int(p["stop_period"]), adjust=False).mean().to_numpy()
    rng = (h - lo).rolling(int(p["range_len"])).mean().to_numpy()
    go = ((ema > sma) & (ema.shift(1) <= sma.shift(1))).to_numpy()
    ev = ema.to_numpy()
    dl = float(p["delta"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    stop_p, inl_p = 0.0, 0
    for i in range(m):
        if go[i] and not inl_p:
            le[i] = i + 1 < m
            inl, stop = 1, ev[i] - dl * rng[i]
        else:
            sp = 0.0 if np.isnan(stop_p) else stop_p
            stop = ev[i] - dl * rng[i] if (ev[i] > sp + dl * rng[i] and inl_p) else sp
            inl = inl_p
            if sv[i] < stop and inl_p:
                lx[i], inl, stop = True, 0, 0.0
        stop_p, inl_p = stop, inl
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
