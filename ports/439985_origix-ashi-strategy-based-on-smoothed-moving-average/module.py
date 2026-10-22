"""Close against a smoothed "Heikin-Ashi" close, long only, 1-hour bars: a close above (3 x open + SMMA 10 of the close) / 4 goes long, a close below it closes.
Port of FMZ strategy #439985 "Origix Ashi Strategy Based on Smoothed Moving Average" (Smoothed Heiken Ashi Strategy).

FMZ source id: 439985

Source
    https://www.fmz.com/strategy/439985 (PineScript v5, FMZ last modified 2024-01-25 15:26:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 126-162), timeframe '' (chart); smoothing 10
    haOpen = security(tf, open);  haClose = (haOpen x 3 + smma(security(tf, close), 10)) / 4;  close > haClose -> entry Buy;  close < haClose -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * An empty timeframe is the chart's own, so the security calls return the bar's open and close.
      The SMMA uses an SMA seed. The two tests cannot share a bar. Long only. No sizing code. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close against a smoothed blend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (3 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439985_origix_smoothed_ha_close_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smoothed_ha_length": [10, 20, 5],
}
DEFAULT_PARAMS = {"smoothed_ha_length": 10}


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
    o, c = bars_df["open"], bars_df["close"]
    hac = (3 * o + _rma(c, int(p["smoothed_ha_length"]))) / 4
    false = pd.Series(False, index=c.index)
    return c > hac, c < hac, false, false.copy()


def portfolio_kwargs(**params):
    return {}
