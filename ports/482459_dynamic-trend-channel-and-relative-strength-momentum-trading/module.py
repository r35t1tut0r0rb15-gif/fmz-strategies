"""Keltner channel (EMA 20, ATR 10 x 1.5) re-entries with RSI 14 extremes, 3-hour bars: the close crossing back over the lower line with RSI under 30 goes long, crossing back under the upper line with RSI over 70 goes short; a long closes when the close crosses under the EMA or RSI is over 50, a short mirrors it.
Port of FMZ strategy #482459 "Dynamic Trend Channel and Relative Strength Momentum Trading Strategy" (Keltner Channel + RSI Strategy).

FMZ source id: 482459

Source
    https://www.fmz.com/strategy/482459 (PineScript v6, FMZ last modified 2025-02-18 15:15:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-164), EMA 20, ATR 10, x 1.5; RSI 14, 70 / 30, exit at 50; 200 % of equity
    crossover(close, lower) and rsi < 30 -> entry Long;  crossunder(close, upper) and rsi > 70 -> entry Short
    crossunder(close, ema) or rsi > 50 -> close Long;  crossover(close, ema) or rsi < 50 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries come before the closes: an entry that reverses a position stands although the other
      side's close is also true on that bar (it acts only on a position held into the bar and not reversed
      on it, as #441963). REVERSAL INTENDED. The 200 % of equity size is sizing. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Keltner re-entries with RSI extremes and mid-line exits.
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

NAME = "fmz_482459_keltner20_reentry_rsi30_70_mid_exit_reversal"
FAMILY = "keltner_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "multiplier": [1.5, 2.0],
    "ema_length": [20, 50],
}
DEFAULT_PARAMS = {"multiplier": 1.5, "ema_length": 20, "atr_length": 10, "rsi_length": 14,
                  "rsi_overbought": 70, "rsi_oversold": 30}


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
    return 100 - 100 / (1 + up / dn)


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ema = c.ewm(span=int(p["ema_length"]), adjust=False).mean()
    atr = _atr(bars_df, int(p["atr_length"]))
    k = float(p["multiplier"])
    up, dn = ema + k * atr, ema - k * atr
    r = _rsi(c, int(p["rsi_length"]))

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    le = xo(c, dn) & (r < float(p["rsi_oversold"]))
    se = xo(up, c) & (r > float(p["rsi_overbought"]))
    lx = xo(ema, c) | (r > 50)
    sx = xo(c, ema) | (r < 50)
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def portfolio_kwargs(**params):
    return {}
