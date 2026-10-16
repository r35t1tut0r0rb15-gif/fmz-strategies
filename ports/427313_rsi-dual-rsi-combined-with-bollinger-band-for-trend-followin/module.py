"""Madrugada: two RSIs and a Bollinger band (20, 1.7): RSI 10 under 30 and RSI 6 under 27 with the
close crossing the lower band goes long; RSI 10 and RSI 6 above 70 with the close crossing the upper
band goes short (always in the market after the first signal).
Port of FMZ strategy #427313 "Dual RSI Combined with Bollinger Band for Trend Following".

FMZ source id: 427313

Source
    https://www.fmz.com/strategy/427313 (PineScript v2, FMZ last modified 2023-09-19 22:10:02).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 124-166), RSI 10 and 6, BB 20 x 1.7
    rsi10 < 30 and rsi6 < 27 and cross(lower, close) -> entry long
    rsi10 > 70 and rsi6 > 70 and cross(upper, close) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * cross() is either direction. The thresholds 30 / 27 / 70 are hard-coded in the entry
      functions (the OSold / OBought inputs are never used).
    * exitLong() (`short < long`, two integer inputs: always true) is defined but never passed to
      an order: no exit other than the opposite entry.
    * stdev is the population standard deviation. strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels, a band in standard deviations.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427313_madrugada_dual_rsi_bb"
FAMILY = "bollinger_reversion"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 40],
    "bb_mult": [1.7, 2.2],
    "rsi1_length": [10, 14],
}
DEFAULT_PARAMS = {"rsi1_length": 10, "rsi2_length": 6, "bb_length": 20, "bb_mult": 1.7}


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


def _rsi(close, n):
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


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
    r1 = _rsi(c, int(p["rsi1_length"]))
    r2 = _rsi(c, int(p["rsi2_length"]))
    n = int(p["bb_length"])
    basis, dev = c.rolling(n).mean(), p["bb_mult"] * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev

    def cross(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))) | ((a < b) & (a.shift(1) >= b.shift(1)))

    long_c = (r1 < 30) & (r2 < 27) & cross(lower, c).to_numpy()
    short_c = (r1 > 70) & (r2 > 70) & cross(upper, c).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
