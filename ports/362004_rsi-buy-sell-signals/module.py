"""Envelope crosses traded as written: close crossing DOWN through the upper envelope goes
LONG, close crossing UP through the lower envelope goes SHORT (always in).
Port of FMZ strategy #362004 "RSI-Buy-Sell-Signals" (ENVELOPE - RSI indicator, orders added).

Source
    https://www.fmz.com/strategy/362004 (PineScript v5, FMZ last modified 2022-05-09 15:14:58).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 66-93), length 8, percent 0.22, source hl2, SMA basis
    upper = sma(hl2,8)*(1+0.22%); lower = sma(hl2,8)*(1-0.22%)
    cross_sell = crossunder(close, upper) -> entry LONG
    else cross_buy = crossover(close, lower) -> entry SHORT
    (the RSI conditions feed labels/alerts only)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the +/-0.22 % envelope becomes +/- `env_atr` x Wilder ATR(14).
    * The variable names say sell/buy but the orders are reversed; ported as written (flagged).
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362004_envelope_cross_faded"
FAMILY = "ma_envelope_reversion"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [8, 14, 20],
    "env_atr": [0.1, 0.25, 0.5],
}
DEFAULT_PARAMS = {"length": 8, "env_atr": 0.25, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    basis = ((bars_df["high"] + bars_df["low"]) / 2).rolling(int(p["length"])).mean()
    band = p["env_atr"] * _atr_pine(bars_df, int(p["atr_length"]))
    upper, lower = basis + band, basis - band
    x_dn_upper = ((c < upper) & (c.shift(1) >= upper.shift(1))).to_numpy()
    x_up_lower = ((c > lower) & (c.shift(1) <= lower.shift(1))).to_numpy()
    return _always_in(x_dn_upper, x_up_lower, bars_df.index)


def portfolio_kwargs(**params):
    return {}
