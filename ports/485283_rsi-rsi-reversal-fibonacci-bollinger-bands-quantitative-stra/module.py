"""RSI 14 entering the 30 / 70 zones, hourly bars: RSI falling to 30 or under goes long, rising to 70 or over goes short; reversing (the per-bar 1 % / 2 % bracket from the current close is pending).
Port of FMZ strategy #485283 "RSI反转斐波那契布林带量化策略-RSI-Reversal-Fibonacci-Bollinger-Bands-Quantitative-Strategy" (BRAHIM KHATTARA).

FMZ source id: 485283

Source
    https://www.fmz.com/strategy/485283 (PineScript v6, FMZ last modified 2025-03-20 11:42:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 180-257), RSI 14 / 30 / 70; stop 1 %; target 2 %; Fibonacci VWMA bands (plots only)
    rsi <= 30 and rsi[1] > 30 -> entry Long;  rsi >= 70 and rsi[1] < 70 -> entry Short
    long -> exit(limit = close x 1.02, stop = close x 0.99) re-sent every bar from the current close;  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels follow the price: not
      ported, mark trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. The
      Fibonacci Bollinger bands use a VWMA but only for plots, so volume reaches no order. An entry on the
      other side reverses (REVERSAL INTENDED). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent close bracket pending.
    2 generic: PASS, RSI zone entries.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_485283_rsi14_into_30_70_zone_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_os": [30, 20],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"rsi_os": 30, "rsi_length": 14}


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
    r = _rsi(c, int(p["rsi_length"]))
    os_ = float(p["rsi_os"])
    ob = 100 - os_
    le = (r <= os_) & (r.shift(1) > os_)
    se = (r >= ob) & (r.shift(1) < ob)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
