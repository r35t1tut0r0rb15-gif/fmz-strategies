"""Ultimate RSI (range-expansion RSI, RMA 14) crossing above its EMA 14 signal below 50 goes long, crossing below it
above 50 goes short, always in, four-hour bars.
Port of FMZ strategy #482453 "基于RSI信号线交叉的多周期趋势跟踪交易策略-Multi-Period-RSI-Signal-Line-Crossover-Trend-Following-Strategy" (Ultimate RSI [LuxAlgo] Strategy).

FMZ source id: 482453

Source
    https://www.fmz.com/strategy/482453 (PineScript v6, FMZ last modified 2025-02-18 15:04:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-173), length 14 (RMA), signal 14 (EMA)
    upper / lower = 14-bar highest / lowest close; diff = upper rose ? range : lower fell ? -range : close change
    arsi = rma(diff, 14) / rma(|diff|, 14) x 50 + 50; signal = ema(arsi, 14)
    crossover(arsi, signal) and arsi < 50 -> close short, entry long
    crossunder(arsi, signal) and arsi > 50 -> close long, entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes repeat the reversal of the entries (REVERSAL INTENDED); always in. The smoothing-method inputs keep
      their defaults (RMA, EMA). Signal module, no stops. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an RSI variant and its signal line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, quoted in original_sizing.txt.
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

NAME = "fmz_482453_ultimate_rsi_signal_cross_always_in"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 28],
    "smooth": [14, 7],
}
DEFAULT_PARAMS = {"length": 14, "smooth": 14}


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
    c = bars_df["close"]
    n = int(p["length"])
    upper, lower = c.rolling(n).max(), c.rolling(n).min()
    rng = upper - lower
    d = c.diff()
    diff = d.where(~(lower < lower.shift(1)), -rng).where(~(upper > upper.shift(1)), rng)
    num, den = _rma(diff, n), _rma(diff.abs(), n)
    arsi = (num / den * 50 + 50).where(den != 0, 50.0).where(den.notna())
    sig = arsi.ewm(span=int(p["smooth"]), adjust=False).mean()
    long_e = ((arsi > sig) & (arsi.shift(1) <= sig.shift(1)) & (arsi < 50)).astype(bool)
    short_e = ((arsi < sig) & (arsi.shift(1) >= sig.shift(1)) & (arsi > 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
