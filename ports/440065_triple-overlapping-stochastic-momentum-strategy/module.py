"""Triple SMI contrarian states, 1-hour bars: all three stochastic momentum indices (10, 20, 5; smoothing 3 / 3) under their EMA 10 signals hold a long, all three above them hold a short; reversing.
Port of FMZ strategy #440065 "Triple Overlapping Stochastic Momentum Strategy" (Stochastic Momentum multi strategy).

FMZ source id: 440065

Source
    https://www.fmz.com/strategy/440065 (PineScript v2, FMZ last modified 2024-01-26 12:15:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 181-279), SMI 10 / 20 / 5, smoothing 3 / 3, signal EMA 10 each; levels 40 / -40 (unused); date inputs unused
    smi = 100 ema(ema(close - (highest(q) + lowest(q)) / 2, 3), 3) / (0.5 ema(ema(highest(q) - lowest(q), 3), 3));  sig = ema(smi, 10)
    long = smi3 < sig3 and smi2 < sig2 and smi < sig -> entry L;  short = all three above -> entry S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signal type is EMA for all three. The overbought / oversold levels feed nothing. A same-side
      entry while in the position is ignored. strategy.entry reverses: REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMI against its signal.
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

NAME = "fmz_440065_triple_smi_below_signal_state"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "nsig": [10, 5],
    "q2": [20, 40],
}
DEFAULT_PARAMS = {"nsig": 10, "q2": 20, "q1": 10, "q3": 5, "r": 3, "s": 3}


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
    r, s, ns = int(p["r"]), int(p["s"]), int(p["nsig"])

    def ee(x):
        return x.ewm(span=r, adjust=False).mean().ewm(span=s, adjust=False).mean()

    below = pd.Series(True, index=c.index)
    above = pd.Series(True, index=c.index)
    for key in ("q1", "q2", "q3"):
        q = int(p[key])
        hh, ll = h.rolling(q).max(), lo.rolling(q).min()
        with np.errstate(divide="ignore", invalid="ignore"):
            smi = 100 * ee(c - 0.5 * (hh + ll)) / (0.5 * ee(hh - ll))
        sig = smi.ewm(span=ns, adjust=False).mean()
        below &= smi < sig
        above &= smi > sig
    false = pd.Series(False, index=c.index)
    return below, false, above, false.copy()


def portfolio_kwargs(**params):
    return {}
