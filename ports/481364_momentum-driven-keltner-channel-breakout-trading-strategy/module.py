"""Keltner channel (EMA 20, ATR 20 x 1.5) breakouts with momentum 14, 15-minute bars: the close crossing over the upper line with positive momentum goes long, under the lower line with negative momentum goes short; the close crossing the middle line or momentum turning against the position closes it; reversing.
Port of FMZ strategy #481364 "Momentum Driven Keltner Channel Breakout Trading Strategy" (Keltner Channels + Momentum Strategy).

FMZ source id: 481364

Source
    https://www.fmz.com/strategy/481364 (PineScript v5, FMZ last modified 2025-02-10 15:03:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 137-194), KC EMA 20, ATR 20 x 1.5; momentum 14; 200 % of equity
    crossover(close, upper) and mom > 0 -> entry Long;  crossunder(close, lower) and mom < 0 -> entry Short;  crossunder(close, ema) or mom < 0 -> close Long;  crossover(close, ema) or mom > 0 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are states (momentum sign) or crossings; a close acts only on the held position and
      leaves a same-bar reversal standing (as #441963). REVERSAL INTENDED. The 200 % of equity size is
      sizing. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Keltner breakouts with momentum confirmation and exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_481364_keltner20_breakout_momentum14_reversal"
FAMILY = "keltner_channel"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length_kc": [20, 50],
    "mult": [1.5, 2.5],
}
DEFAULT_PARAMS = {"length_kc": 20, "mult": 1.5, "mom_length": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length_kc"])
    mid = c.ewm(span=n, adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, n)
    k = float(p["mult"])
    up, dn = mid + k * atr, mid - k * atr
    mom = c - c.shift(int(p["mom_length"]))
    le = (c > up) & (c.shift(1) <= up.shift(1)) & (mom > 0)
    se = (c < dn) & (c.shift(1) >= dn.shift(1)) & (mom < 0)
    lx = (((c < mid) & (c.shift(1) >= mid.shift(1))) | (mom < 0)) & ~se
    sx = (((c > mid) & (c.shift(1) <= mid.shift(1))) | (mom > 0)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
