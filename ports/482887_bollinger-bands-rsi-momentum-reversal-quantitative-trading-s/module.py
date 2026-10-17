"""Bollinger(20, 2) re-entries with RSI 14 extremes, closed when the close crosses the middle band, 1-hour bars: the
close crossing back above the lower band with RSI below 30 goes long; crossing back below the upper band with RSI above
70 goes short; any cross of the middle band closes the position.
Port of FMZ strategy #482887 "Bollinger-Bands与RSI结合的动量反转量化交易策略-Momentum-Reversal-Quantitative-Trading-Strategy-Combining-Bollinger-Bands-and-RSI" (Bollinger Bands + RSI Strategy).

FMZ source id: 482887

Source
    https://www.fmz.com/strategy/482887 (PineScript v5, FMZ last modified 2025-02-20 16:38:15).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 132-164), BB 20 x 2, RSI 14 (30 / 70)
    buy = crossover(close, lower) and rsi < 30; sell = crossunder(close, upper) and rsi > 70
    exit = cross(close, basis) -> close long and close short (after the entries)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes act on the position held at the bar's start and never undo that bar's entry (as #430850).
      Target-position state machine, exits only on going flat. ta.stdev population.
    * Entries reverse (REVERSAL INTENDED). No stops. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_482887_bollinger_rsi_reentry_mid_exit"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [2.0, 2.5],
    "rsi_os": [30, 35],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_len": 14, "rsi_os": 30}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


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
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), p["mult"] * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    rsi = _rsi(c, int(p["rsi_len"]))
    buy = ((c > dn) & (c.shift(1) <= dn.shift(1)) & (rsi < p["rsi_os"])).to_numpy()
    sell = ((c < up) & (c.shift(1) >= up.shift(1)) & (rsi > 100 - p["rsi_os"])).to_numpy()
    cross = (((c > basis) & (c.shift(1) <= basis.shift(1))) | ((c < basis) & (c.shift(1) >= basis.shift(1)))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i]:
            pos = 1
        if sell[i]:
            pos = -1
        if cross[i] and start != 0 and pos == start:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
