"""Bollinger 20 / 2 band re-entries with RSI 14 extremes, hourly bars: the close crossing back over the lower band with RSI under 30 goes long, back under the upper band with RSI over 70 goes short; the close crossing the basis closes either; reversing.
Port of FMZ strategy #482887 "Bollinger-Bands与RSI结合的动量反转量化交易策略-Momentum-Reversal-Quantitative-Trading-Strategy-Combining-Bollinger-Bands-and-RSI" (Bollinger Bands + RSI Strategy).

FMZ source id: 482887

Source
    https://www.fmz.com/strategy/482887 (PineScript v5, FMZ last modified 2025-02-20 16:38:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-169), Bollinger 20 x 2.0; RSI 14 / 30 / 70
    crossover(close, lower) and rsi < 30 -> entry Buy;  crossunder(close, upper) and rsi > 70 -> entry Sell
    cross(close, basis) -> close Buy, close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close on the bar of an entry is masked by the entry; an entry on the other side reverses
      (REVERSAL INTENDED). The RSI plot offset is drawing only. No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger band re-entries with RSI extremes.
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

NAME = "fmz_482887_bb20_2_reentry_rsi14_30_70_basis_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 40],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "rsi_length": 14}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper, lower = basis + float(p["mult"]) * sd, basis - float(p["mult"]) * sd
    r = _rsi(c, int(p["rsi_length"]))
    le = (c > lower) & (c.shift(1) <= lower.shift(1)) & (r < 30)
    se = (c < upper) & (c.shift(1) >= upper.shift(1)) & (r > 70)
    x = ((c > basis) & (c.shift(1) <= basis.shift(1))) | ((c < basis) & (c.shift(1) >= basis.shift(1)))
    return le, x & ~le & ~se, se, x & ~se & ~le


def portfolio_kwargs(**params):
    return {}
