"""Fractal breakouts, 1-hour bars: the close crossing over the second-latest up fractal (a high with two lower highs after it and two to six before) goes long, crossing under the second-latest down fractal
goes short; reversing.
Port of FMZ strategy #440439 "Double Fractal Breakout Strategy" (Fractal Breakout Strategy).

FMZ source id: 440439

Source
    https://www.fmz.com/strategy/440439 (PineScript v4, FMZ last modified 2024-01-30 15:53:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-132), fractal tests with up to six bars before the centre (equal highs allowed in the inner bars)
    FUp = high[2] above high[1], high[0] and high[3], high[4] (or the 5- to 8-bar variants with <= on the inner bars);  FractalUp = valuewhen(FUp, high[2], 1)  (FDown mirrored with lows)
    crossover(close, FractalUp) -> entry Long;  crossunder(close, FractalDown) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A fractal is confirmed two bars after its centre (the tests read high[2] .. high[0]), so it uses
      past bars. valuewhen(.., 1) is the second most recent confirmed fractal, as written.
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fractals confirmed from past bars.
    2 generic: PASS, fractal levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440439_second_fractal_breakout"
FAMILY = "fractal_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "occurrence": [1, 0],
}
DEFAULT_PARAMS = {"occurrence": 1}


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


def _fractal(x, up):
    """The script's five fractal tests (k = 0 .. 4 extra bars before the centre x[2])."""
    c2 = x.shift(2)

    def beats(k, strict):
        y = x.shift(k)
        if up:
            return (y < c2) if strict else (y <= c2)
        return (y > c2) if strict else (y >= c2)

    out = pd.Series(False, index=x.index)
    for k in range(5):
        t = beats(4 + k, True) & beats(3 + k, True) & beats(1, True) & beats(0, True)
        for j in range(3, 3 + k):
            t &= beats(j, False)
        out |= t
    return out


def _valuewhen(cond, val, occ):
    cv, vv = cond.to_numpy(dtype=bool), val.to_numpy(dtype=float)
    out = np.full(len(cv), np.nan)
    hist = []
    for i in range(len(cv)):
        if cv[i]:
            hist.append(vv[i])
        if len(hist) > occ:
            out[i] = hist[-1 - occ]
    return pd.Series(out, index=cond.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    occ = int(p["occurrence"])
    fu = _valuewhen(_fractal(h, True), h.shift(2), occ)
    fd = _valuewhen(_fractal(lo, False), lo.shift(2), occ)
    up = (c > fu) & (c.shift(1) <= fu.shift(1))
    dn = (c < fd) & (c.shift(1) >= fd.shift(1))
    false = pd.Series(False, index=c.index)
    return up & ~dn, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
