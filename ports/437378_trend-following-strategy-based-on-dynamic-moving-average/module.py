"""ALMA baselines of highs and lows, 1-hour bars: ohlc4 above the ALMA 55 of highs goes long, under the ALMA 55 of lows goes short (entries sent on every such bar), reversing; in between nothing is sent.
Port of FMZ strategy #437378 "Trend Following Strategy Based on Dynamic Moving Average" (Baseline Strategy - evo).

FMZ source id: 437378

Source
    https://www.fmz.com/strategy/437378 (PineScript v4, FMZ last modified 2024-01-02 10:44:53).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 132-191), MA type ALMA, length 55, source ohlc4, offset 0.85, sigma 10; current resolution
    baselinehigh / baselinelow = ma(high / low, 55) of the chosen type;  mtfhigh / mtflow = security(tickerid, current resolution, ...)
    long = ohlc4 > mtfhigh -> entry Long;  short = ohlc4 < mtflow -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The resolution is the chart's own (useCurrentRes true), so security() returns the series itself. ALMA
      weights the window oldest to newest with a Gaussian centred at offset x (window - 1), sigma window /
      sigma, as Pine. SMA, EMA, WMA, HMA and RMA are ported too; VWMA needs volume and is left out (check 8;
      not the default). A same-side entry while in the position is ignored (pyramiding 0). REVERSAL
      INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against average baselines.
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

NAME = "fmz_437378_alma_high_low_baseline"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "baseline": [55, 30],
    "sigma": [10.0, 6.0],
}
DEFAULT_PARAMS = {"baseline": 55, "sigma": 10.0, "offset": 0.85, "ma_type": "ALMA"}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _alma(x, n, offset, sigma):
    m = offset * (n - 1)
    s = n / sigma
    w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))     # oldest first, as Pine's loop
    w = w / w.sum()
    return x.rolling(n).apply(lambda v: np.dot(v, w), raw=True)


def _ma(x, n, kind, p):
    if kind == "SMA":
        return x.rolling(n).mean()
    if kind == "EMA":
        return x.ewm(span=n, adjust=False).mean()
    if kind == "WMA":
        return _wma(x, n)
    if kind == "HMA":
        return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(round(np.sqrt(n))))
    if kind == "RMA":
        return _rma(x, n)
    if kind == "ALMA":
        return _alma(x, n, float(p["offset"]), float(p["sigma"]))
    raise ValueError(f"MA type {kind!r} not ported (VWMA needs volume, check 8)")


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["baseline"])
    bh = _ma(h, n, p["ma_type"], p)
    bl = _ma(lo, n, p["ma_type"], p)
    src = (o + h + lo + c) / 4
    false = pd.Series(False, index=bars_df.index)
    return src > bh, false, src < bl, false.copy()


def portfolio_kwargs(**params):
    return {}
