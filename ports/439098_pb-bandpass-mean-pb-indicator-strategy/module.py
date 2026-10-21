"""Ehlers' super passband crossings of its RMS bands, 30-minute bars: the passband rising against 5 bars ago while crossing up through -RMS, 0 or +RMS goes long; falling while crossing down through +RMS, 0 or
-RMS goes short; reversing.
Port of FMZ strategy #439098 "布林带穿越均值PB指标策略Bandpass-Mean-PB-Indicator-Strategy" (BandPass EOS).

FMZ source id: 439098

Source
    https://www.fmz.com/strategy/439098 (PineScript v4, FMZ last modified 2024-01-17 17:10:53).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 139-207), source close; fast 41, slow 54; additional triggers on (unused); date window true
    PB = (a1 - a2) src + (a2 (1 - a1) - a1 (1 - a2)) src[1] + (2 - a1 - a2) PB[1] - (1 - a1)(1 - a2) PB[2] (a1 = 5 / 41, a2 = 5 / 54, after bar 41);  RMS = sqrt(sum of PB[i]^2, i = 0..49 / 40)
    buy = PB > PB[5] and (crossover(PB, -RMS) or crossover(PB, RMS) or crossover(PB, 0)) -> entry long;  sell mirror -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * PB is 0 (and RMS 0) until bar 42; the RMS sums the last 50 values divided by 40, as written, and is
      na while fewer than 50 bars exist. testPeriod() is true. strategy.entry reverses: REVERSAL INTENDED.
      The capital is sizing. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, passband filter and RMS crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital stored.
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

NAME = "fmz_439098_super_passband_rms_cross"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period1": [41, 20],
    "period2": [54, 40],
}
DEFAULT_PARAMS = {"period1": 41, "period2": 54}


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
    sv = c.to_numpy(dtype=float)
    p1, p2 = int(p["period1"]), int(p["period2"])
    a1, a2 = 5.0 / p1, 5.0 / p2
    m = len(sv)
    pb = np.zeros(m)
    rms = np.zeros(m)
    for i in range(m):
        if i > p1:
            pb1 = pb[i - 1]
            pb2 = pb[i - 2] if i > 1 else 0.0
            pb[i] = ((a1 - a2) * sv[i] + (a2 * (1 - a1) - a1 * (1 - a2)) * sv[i - 1]
                     + (2 - a1 - a2) * pb1 - (1 - a1) * (1 - a2) * pb2)
            rms[i] = np.sqrt(np.sum(pb[i - 49:i + 1] ** 2) / 40) if i >= 49 else np.nan
    ps, rs = pd.Series(pb, index=c.index), pd.Series(rms, index=c.index)
    rising = ps > ps.shift(5)
    falling = ps < ps.shift(5)
    zero = pd.Series(0.0, index=c.index)

    def _xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def _xu(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    buy = rising & (_xo(ps, -rs) | _xo(ps, rs) | _xo(ps, zero))
    sell = falling & (_xu(ps, rs) | _xu(ps, -rs) | _xu(ps, zero))
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
