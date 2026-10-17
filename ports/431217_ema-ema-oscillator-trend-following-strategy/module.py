"""Azzrael's EMA oscillator, 1-hour bars, long only: the close-minus-EMA 200 line crossing under -1.7 times its own 200-bar
deviation (entering the oversold zone) goes long; the line crossing zero closes the long. Adds are not ported.
Port of FMZ strategy #431217 "基于EMA指标的趋势追踪策略EMA-Oscillator-Trend-Following-Strategy" (STR:EMA Oscilator [Azzrael]).

FMZ source id: 431217

Source
    https://www.fmz.com/strategy/431217 (PineScript v5, FMZ last modified 2023-11-06 09:53:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 195-227), EMA 200, factor 1.7, model "Buy on enter to OverSell", pyramiding 3
    v = close - ema(close, 200); dev = stdev(v, 200); dev_limit = -1.7 dev
    crossunder(v, dev_limit) -> entry "Buy" (adds up to pyramiding 3);  cross(v, 0) -> close "Buy"

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding 3: further signals add in the source; adds are not ported (one net position). The
      close is written after the entry and acts on the position held at the bar's start (a bar that
      meets both ends flat when already long, long when flat). The "OverBuy" model is off by default.
    * stdev is the population deviation. Long only; Opposite entries cannot occur. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; adds not ported.
    2 generic: PASS, a deviation-scaled oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 30 % of equity and pyramiding 3 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431217_ema_oscillator_oversold_long"
FAMILY = "zscore_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [200, 100],
    "factor": [1.7, 2.5],
}
DEFAULT_PARAMS = {"ema_len": 200, "factor": 1.7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["ema_len"])
    v = c - c.ewm(span=n, adjust=False).mean()
    lim = -v.rolling(n).std(ddof=0) * float(p["factor"])
    buy = ((v < lim) & (v.shift(1) >= lim.shift(1))).to_numpy()
    v1 = v.shift(1)
    out = (((v > 0) & (v1 <= 0)) | ((v < 0) & (v1 >= 0))).to_numpy()
    m = len(buy)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if start == 1 and out[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
