"""Absolute price oscillator (HPotter APO 2.0): EMA 10 minus EMA 20 above a buy zone goes long, below
a sell zone goes short (always in the market after the first signal).
Port of FMZ strategy #427479 "Absolute Price Oscillator Trend Following Strategy".

FMZ source id: 427479

Source
    https://www.fmz.com/strategy/427479 (PineScript v2, FMZ last modified 2023-09-21 15:27:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 178-198), EMA 10 / 20, zones +3 / -3, reverse off
    apo = ema(close, 10) - ema(close, 20)
    pos = apo > 3 ? 1 : apo < -3 ? -1 : pos[1] -> entries on pos

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the zones +-3 are price units (instrument-specific); they become
      +- `zone_atr` x Wilder ATR(14). On the source's 4-hour BTC bars 3 USD is a tiny fraction of an
      ATR (about 0.01-0.02), i.e. close to the sign of the APO; the grid brackets it.
    * strategy.entry reverses: REVERSAL INTENDED; "Trade reverse" is off.
    * FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit zones -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: ND427479 (with #442834, Jaccard 0.756); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427479_hpotter_apo"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "zone_atr": [0.02, 0.1, 0.3],
    "long_ema": [20, 40],
}
DEFAULT_PARAMS = {"short_ema": 10, "long_ema": 20, "zone_atr": 0.02, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    apo = (c.ewm(span=int(p["short_ema"]), adjust=False).mean()
           - c.ewm(span=int(p["long_ema"]), adjust=False).mean()).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    zone = (p["zone_atr"] * _rma(tr, int(p["atr_length"]))).to_numpy()
    m = len(apo)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if apo[i] > zone[i]:
            pos = 1
        elif apo[i] < -zone[i]:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
