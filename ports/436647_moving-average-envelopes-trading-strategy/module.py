"""Moving-average envelope side, 1-hour bars: a close over the SMA 14 plus 1 % is long; a close under the SMA minus 1 % is short (reversing); inside the envelope the earlier state holds; an optional switch trades the reverse.
Port of FMZ strategy #436647 "Moving Average Envelopes Trading Strategy" (Moving Average Envelopes).

FMZ source id: 436647

Source
    https://www.fmz.com/strategy/436647 (PineScript v2, FMZ last modified 2023-12-26 15:55:43).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 187-203), length 14, shift 1 %, reverse off
    xHighBand = sma(close, 14) x 1.01;  xLowBand = sma(close, 14) x 0.99;  pos = 1 if close > xHighBand, -1 if close < xLowBand, else pos[1];  possig = -pos when reverse;  entry Long / Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is a level, so the entry is sent on every bar of the state; a same-side entry while in the
      position is ignored (pyramiding 0). REVERSAL INTENDED. The default quantity is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, envelope breakout state.
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

NAME = "fmz_436647_ma_envelope_state"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "percent_shift": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 14, "percent_shift": 1.0, "reverse": False}


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
    sma = c.rolling(int(p["length"])).mean()
    shift = float(p["percent_shift"]) / 100.0
    hi, lo = (sma * (1.0 + shift)).to_numpy(), (sma * (1.0 - shift)).to_numpy()
    cc = c.to_numpy()
    m = len(cc)
    pos = np.zeros(m)
    prev = 0.0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if cc[i] > hi[i]:
                prev = 1.0
            elif cc[i] < lo[i]:
                prev = -1.0
            pos[i] = prev
    sig = -pos if p["reverse"] else pos
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(sig == 1, index=ix), false, pd.Series(sig == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
