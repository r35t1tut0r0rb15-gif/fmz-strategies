"""RSI(2) extremes around a 70-bar SMA, as written: short overbought ABOVE the MA, long
oversold BELOW it (the reverse of Connors' published rule).
Port of FMZ strategy #207157 "Larry-Connors-RSI2均值回归策略" (Larry Connors RSI2 mean reversion).

Source
    https://www.fmz.com/strategy/207157 (MyLanguage, author "homily", FMZ last modified
    2020-05-14 09:50:47). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 38-52), Y 70
    RSI2 = SMA(MAX(C-REF(C,1),0),2,1) / SMA(ABS(C-REF(C,1)),2,1) * 100;  ma1 = MA(C,Y)
    C>ma1 AND RSI2>90 -> SK;   C>ma1 AND RSI2<10 -> BP
    C<ma1 AND RSI2<10 -> BK;   C<ma1 AND RSI2>90 -> SP
    AUTOFILTER

Interpretation choices (MyLanguage rules in SURVEY_README.md)
    * Close-price model, completed bars, one signal per bar in source order; entries only from
      flat (AUTOFILTER). Opposite entries cannot occur; portfolio_kwargs also returns
      upon_opposite_entry="ignore" (rule 6).
    * The exits are conditional on the MA side too (BP needs C>ma1, SP needs C<ma1), so a short
      stays open while price is below the MA. Ported as written.
    * The linked articles describe Connors' rule (long above the 200-day MA on RSI2<10); the
      code does the opposite. The port follows the code; flagged in PORT_NOTES.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_207157_rsi2_extremes_vs_sma"
FAMILY = "rsi_oscillator"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "y": [50, 70, 100, 200],
    "band": [5.0, 10.0],
}
DEFAULT_PARAMS = {"y": 70, "band": 10.0, "rsi_length": 2}


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
    dc = c.diff()
    a = 1 / p["rsi_length"]
    rsi = (dc.clip(lower=0).ewm(alpha=a, adjust=False, ignore_na=True).mean()
           / dc.abs().ewm(alpha=a, adjust=False, ignore_na=True).mean() * 100)
    ma = c.rolling(int(p["y"])).mean()
    lo_b, hi_b = p["band"], 100 - p["band"]
    above, below = (c > ma).to_numpy(), (c < ma).to_numpy()
    r = rsi.to_numpy()

    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if pos == 0 and above[i] and r[i] > hi_b:            # SK
            se[i], pos = True, -1
        elif pos == -1 and above[i] and r[i] < lo_b:         # BP
            sx[i], pos = True, 0
        elif pos == 0 and below[i] and r[i] < lo_b:          # BK
            le[i], pos = True, 1
        elif pos == 1 and below[i] and r[i] > hi_b:          # SP
            lx[i], pos = True, 0

    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
