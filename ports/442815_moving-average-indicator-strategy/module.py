"""HPotter overbought / oversold, 1-hour bars: the stochastic(10) as a fraction, flipped when the close is not above the close 10 bars back; above 0.92 holds long, under 0.5 holds short; reversing.
Port of FMZ strategy #442815 "Moving Average Indicator Strategy" (Overbought/Oversold (OB/OS)).

FMZ source id: 442815

Source
    https://www.fmz.com/strategy/442815 (PineScript v2, FMZ last modified 2024-02-26 11:10:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-172), length 10; buy band 0.92, sell band 0.5; reverse off
    xOBOS = stoch(close, high, low, 10);  nRes = close > close[10] ? xOBOS / 100 : (100 - xOBOS) / 100;  pos = nRes < 0.5 ? -1 : nRes > 0.92 ? 1 : pos[1];  pos 1 -> entry Long, -1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level; the entries repeat while it holds and are refused while held.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic band state.
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

NAME = "fmz_442815_hpotter_obos_stoch_band_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "buy_band": [0.92, 0.8],
}
DEFAULT_PARAMS = {"length": 10, "buy_band": 0.92, "sell_band": 0.5, "reverse": False}


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
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    res = pd.Series(np.where(c > c.shift(n), k / 100, (100 - k) / 100), index=c.index).where(k.notna())
    rv = res.to_numpy()
    sb, bb = float(p["sell_band"]), float(p["buy_band"])
    m = len(rv)
    pos = np.zeros(m, dtype=np.int8)
    s = 0
    for i in range(m):
        if rv[i] < sb:
            s = -1
        elif rv[i] > bb:
            s = 1
        pos[i] = s
    if p["reverse"]:
        pos = -pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(pos == 1, index=ix), false, pd.Series(pos == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
