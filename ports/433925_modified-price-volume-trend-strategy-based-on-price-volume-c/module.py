"""HPotter's modified price-volume trend (a running sum of volume / 50000 x the ohlc4 change in percent) above its SMA 23 goes long, below it goes short; 3-hour bars, reversing.
Port of FMZ strategy #433925 "Modified Price Volume Trend Strategy Based on Price Volume Changes" (Modified Price-Volume Trend Backtest (HPotter)).

FMZ source id: 433925

Source
    https://www.fmz.com/strategy/433925 (PineScript v2, FMZ last modified 2023-12-01 14:56:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 164-182), Level 0, Scale 1, Length 23; volume / 50000; reverse off
    xCumPVT = nz(xCumPVT[1]) + volume / 50000 x (ohlc4 - ohlc4[1]) / ohlc4[1];  nRes = 0 + 1 x xCumPVT;  pos = nRes > sma(nRes, 23) ? 1 : nRes < sma ? -1 : pos[1]
    pos 1 -> entry Long;  pos -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 1 / 50000 factor and the running sum's start leave the comparison with its own SMA unchanged,
      so only the volume's shape matters. reverse is off. REVERSAL INTENDED. No sizing code. FREQ = "3h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price-volume trend against its average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the cumulative price-volume trend; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433925_modified_price_volume_trend_sma23_state_reversal"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [23, 50],
}
DEFAULT_PARAMS = {"length": 23}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    x = (o + h + lo + c) / 4
    term = (v / 50000.0 * (x - x.shift(1)) / x.shift(1)).to_numpy(dtype=float)
    m = len(term)
    cum = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        cum[i] = (0.0 if np.isnan(prev) else prev) + term[i]
        prev = cum[i]
    nres = pd.Series(cum, index=c.index)
    ma = nres.rolling(int(p["length"])).mean()
    raw = np.where(nres > ma, 1, np.where(nres < ma, -1, 0))
    pos = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if raw[i] != 0:
            q = raw[i]
        pos[i] = q
    prv = np.concatenate(([0], pos[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((pos == 1) & (prv != 1), index=ix), false,
            pd.Series((pos == -1) & (prv != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
