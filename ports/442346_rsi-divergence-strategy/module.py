"""RSI 14 divergences at extremes, 1-minute bars: a new 14-bar low with the RSI above its prior 14-bar low and under 30 goes long, closed when the RSI is over 70; a new 14-bar high with the RSI under its
prior high and over 70 goes short, closed when the RSI is under 30; reversing.
Port of FMZ strategy #442346 "RSI Divergence Strategy" (RSI Divergence Strategy).

FMZ source id: 442346

Source
    https://www.fmz.com/strategy/442346 (PineScript v5, FMZ last modified 2024-02-21 11:43:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 182-221), RSI 14; levels 70 / 30
    bull = low < lowest(low, 14)[1] and rsi > lowest(rsi, 14)[1];  long = bull and rsi < 30 -> entry;  rsi > 70 -> close long
    bear = high > highest(high, 14)[1] and rsi < highest(rsi, 14)[1];  short = bear and rsi > 70 -> entry;  rsi < 30 -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close acts only on the held position; a close written after a reversing entry leaves the
      reversal standing (as #438020). strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, price / RSI divergence at extremes.
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

NAME = "fmz_442346_rsi14_extreme_divergence_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 9],
    "oversold": [30, 20],
}
DEFAULT_PARAMS = {"rsi_length": 14, "oversold": 30}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["rsi_length"])
    r = _rsi(c, n)
    os_ = float(p["oversold"])
    ob = 100 - os_
    bull = (lo < lo.rolling(n).min().shift(1)) & (r > r.rolling(n).min().shift(1))
    bear = (h > h.rolling(n).max().shift(1)) & (r < r.rolling(n).max().shift(1))
    el, es = (bull & (r < os_)).to_numpy(), (bear & (r > ob)).to_numpy()
    xl, xs = (r > ob).to_numpy(), (r < os_).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    for i in range(m):
        new = held
        if el[i] and new != 1:
            new = 1
        if xl[i] and held == 1 and new == 1:
            new = 0
        if es[i] and new != -1:
            new = -1
        if xs[i] and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
