"""CCI 10 zero crossings after RSI 14 extremes, 1-hour bars: a CCI crossing of zero (either way) with the RSI at or under 35 within the last 4 bars and turning up goes long; with the RSI at or over 65 within 4 bars and turning down it goes short; reversing.
Port of FMZ strategy #454730 "CCI动量背离趋势交易策略CCI-Momentum-Divergence-Trend-Trading-Strategy" (bayush (CCI momentum divergence)).

FMZ source id: 454730

Source
    https://www.fmz.com/strategy/454730 (PineScript v5, FMZ last modified 2024-06-21 14:07:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 196-236), CCI 10 (source 'CCI'); RSI 14, levels 65 / 35; divergence = RSI turn
    cross(cci, 0) and rsi <= 35 in the last 4 bars and rsi > rsi[1] < rsi[2] -> entry Buy;  cross(0, cci) and rsi >= 65 in the last 4 bars and rsi < rsi[1] > rsi[2] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross is either direction, so 'crossUp' and 'crossDown' are the same event: any zero crossing
      of the CCI; the RSI turn decides the side (the two turns cannot meet on one bar). ta.cci divides
      by 0.015 x the mean absolute deviation. There is no exit: positions end at the opposite entry.
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI zero crossings after RSI extremes.
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

NAME = "fmz_454730_cci_zero_cross_rsi_extreme_turn_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [10, 20],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"cci_len": 10, "rsi_len": 14, "ob": 65.0, "os": 35.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["cci_len"])
    sma = c.rolling(n).mean()
    mad = c.rolling(n).apply(lambda v: np.abs(v - v.mean()).mean(), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (c - sma) / (0.015 * mad)
    crossed = ((cci > 0) & (cci.shift(1) <= 0)) | ((cci < 0) & (cci.shift(1) >= 0))
    r = _rsi(c, int(p["rsi_len"]))
    os_, ob = float(p["os"]), float(p["ob"])
    oversold = (r <= os_) | (r.shift(1) <= os_) | (r.shift(2) <= os_) | (r.shift(3) <= os_)
    overbought = (r >= ob) | (r.shift(1) >= ob) | (r.shift(2) >= ob) | (r.shift(3) >= ob)
    bull = (r > r.shift(1)) & (r.shift(1) < r.shift(2))
    bear = (r < r.shift(1)) & (r.shift(1) > r.shift(2))
    le = crossed & oversold & bull
    se = crossed & overbought & bear
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
