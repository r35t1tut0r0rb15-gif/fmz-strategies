"""UT Bot ATR trailing-line crossings, 10-minute bars: the close crossing over the UT Bot line (key 1 x ATR 10) goes long and crossing under goes short, each signal also closing the opposite position; reversing.
Port of FMZ strategy #437649 "Quant Trend Following Strategy" (Combined Strategy).

FMZ source id: 437649

Source
    https://www.fmz.com/strategy/437649 (PineScript v4, FMZ last modified 2024-01-04 15:25:42).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 165-239), EMAs 13 / 50 / 100 / 200 and LinReg candles plotted only; UT Bot key 1, ATR 10, Heikin-Ashi signals off
    xATRTrailingStop ratchets: above the stop on both bars -> max(prev, src - nLoss); below on both -> min(prev, src + nLoss); else src -+ nLoss (nz seeds 0)
    buy = src > stop and crossover(ema(src, 1), stop) -> entry Buy, close Sell;  sell = src < stop and crossover(stop, ema(src, 1)) -> entry Sell, close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * ema(src, 1) is the close itself. The trailing line is followed with the script's nz() seeds (0 on the
      first bar). The EMA lines and LinReg candles are plotted only; Heikin-Ashi signals are off. Orders
      follow the script's call order; each signal reverses. REVERSAL INTENDED. No sizing code. FREQ =
      "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing line.
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

NAME = "fmz_437649_ut_bot_atr_line_cross"
FAMILY = "atr_trailing_line"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [1.0, 2.0],
    "atr_period": [10, 20],
}
DEFAULT_PARAMS = {"key": 1.0, "atr_period": 10}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    nloss = (float(p["key"]) * _rma(tr, int(p["atr_period"]))).to_numpy()
    src = c.to_numpy(dtype=float)
    m = len(src)
    ts = np.full(m, np.nan)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            prev = ts[i - 1] if i and not np.isnan(ts[i - 1]) else 0.0
            s1 = src[i - 1] if i else np.nan
            if src[i] > prev and s1 > prev:
                ts[i] = max(prev, src[i] - nloss[i]) if not np.isnan(nloss[i]) else np.nan
            elif src[i] < prev and s1 < prev:
                ts[i] = min(prev, src[i] + nloss[i]) if not np.isnan(nloss[i]) else np.nan
            else:
                ts[i] = src[i] - nloss[i] if src[i] > prev else src[i] + nloss[i]
    t = pd.Series(ts, index=c.index)
    above = (c > t) & (c.shift(1) <= t.shift(1))
    below = (t > c) & (t.shift(1) <= c.shift(1))
    buy = (c > t) & above
    sell = (c < t) & below
    return buy, sell, sell.copy(), buy.copy()


def portfolio_kwargs(**params):
    return {}
