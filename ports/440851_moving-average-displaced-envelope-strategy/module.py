"""Displaced EMA envelope reversion, 1-minute bars: a close under the EMA 9 of 13 bars ago less 0.5 % goes long, a close over it plus 0.5 % short; the state holds until the other band; reversing.
Port of FMZ strategy #440851 "Moving Average Displaced Envelope Strategy" (MA DE).

FMZ source id: 440851

Source
    https://www.fmz.com/strategy/440851 (PineScript v4, FMZ last modified 2024-02-02 17:02:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-197), EMA 9 on close; 0.5 % above / below; displacement 13; reverse off
    top = ema9[13] x 1.005;  bott = ema9[13] x 0.995;  pos = close < bott ? 1 : close > top ? -1 : pos[1];  1 -> entry Long, -1 -> entry Short, 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The envelope uses the EMA 13 bars back (past values). The state is a level. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, displaced EMA envelope.
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

NAME = "fmz_440851_displaced_ema_envelope_reversion"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "per": [0.5, 1.0],
    "disp": [13, 5],
}
DEFAULT_PARAMS = {"per": 0.5, "disp": 13, "period": 9, "reverse": False}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = c.ewm(span=int(p["period"]), adjust=False).mean().shift(int(p["disp"]))
    f = float(p["per"]) / 100
    lo_b, hi_b = (c < e * (1 - f)).to_numpy(), (c > e * (1 + f)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lo_b[i]:
            pos = 1
        elif hi_b[i]:
            pos = -1
        tgt[i] = pos
    if p["reverse"]:
        tgt = -tgt
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
