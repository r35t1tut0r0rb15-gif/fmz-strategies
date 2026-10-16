"""MACD histogram thrust, hourly bars: the histogram more than a tolerance above its lowest value of the
previous 6 bars goes long, more than the tolerance below its highest value goes short.
Port of FMZ strategy #428783 "Adaptive Multi Timeframe Moving Average Crossover Strategy" (Riz Coloured MACD).

FMZ source id: 428783

Source
    https://www.fmz.com/strategy/428783 (PineScript v3, FMZ last modified 2023-10-09 14:56:37).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-204), EMA 21 / 55, signal EMA 9, 6 bars back, tolerance 4 (price units)
    hist = (ema(close,21) - ema(close,55)) - ema(that, 9)
    hist - lowest(hist, 6)[1] > 4 -> entry long; highest(hist, 6)[1] - hist > 4 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the tolerance of 4 price units becomes tol_atr x Wilder ATR(14) of the same bar;
      4 USD on hourly BTC is about 0.02 ATR (judgement before any backtest).
    * lowest / highest(hist, 6)[1] cover the 6 bars before the current one.
    * The strategy() line is commented out; the defaults apply (bar-close orders).
    * strategy.entry reverses: REVERSAL INTENDED; same-direction entries while in a position are
      ignored. If both tests pass on one bar, the long (first order) is kept. FREQ = "1h".

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, the price-unit tolerance -> an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() line stored.
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

NAME = "fmz_428783_macd_hist_thrust"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tol_atr": [0.02, 0.1],
    "lookback": [6, 10],
}
DEFAULT_PARAMS = {"fast": 21, "slow": 55, "signal": 9, "lookback": 6, "tol_atr": 0.02, "atr_length": 14}


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
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    macd = e(c, p["fast"]) - e(c, p["slow"])
    hist = macd - e(macd, p["signal"])
    n = int(p["lookback"])
    hh, ll = hist.rolling(n).max().shift(1), hist.rolling(n).min().shift(1)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tol = p["tol_atr"] * _rma(tr, int(p["atr_length"]))
    long_e = ((hist - ll) > tol).astype(bool)
    short_e = (((hh - hist) > tol) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
