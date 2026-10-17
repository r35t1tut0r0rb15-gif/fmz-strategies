"""CCI zero crosses after RSI extremes, 1-hour bars: a CCI 10 zero cross (either way, as written) within 4 bars of RSI 14 at or
under 35, with the RSI turning up and the close at or under the EMA 100, goes long; a zero cross within 4 bars of RSI at
or over 65, with the RSI turning down and the close at or over the EMA 100, goes short (reversing).
Port of FMZ strategy #435234 "Reverasal Indicator Strategy" (Reversal Indicator Strategy).

FMZ source id: 435234

Source
    https://www.fmz.com/strategy/435234 (PineScript v5, FMZ last modified 2023-12-13 14:45:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 150-221), entry source CCI 10; divergence on; RSI 14, 65 / 35; EMA 100; mean-reversion bands plotted off
    long = cross(cci, 0) and rsi <= 35 in the last 4 bars and rsi > rsi[1] < rsi[2] and close <= ema100 -> entry long
    short = cross(0, cci) and rsi >= 65 in the last 4 bars and rsi < rsi[1] > rsi[2] and close >= ema100 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross is true for a cross in either direction, so both sides use any zero cross of the CCI,
      as written. CCI uses the mean absolute deviation (Pine's). strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI, RSI and an average.
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

NAME = "fmz_435234_cci_cross_rsi_extreme_turn"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [10, 20],
    "ob": [65, 75],
}
DEFAULT_PARAMS = {"cci_len": 10, "rsi_len": 14, "ob": 65, "ema_len": 100}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(c, n):
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    return (c - ma) / (0.015 * md.replace(0.0, np.nan))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cci = _cci(c, int(p["cci_len"]))
    cross = ((cci > 0) & (cci.shift(1) <= 0)) | ((cci < 0) & (cci.shift(1) >= 0))
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    ob = float(p["ob"])
    os_ = 100 - ob
    os_ago = pd.concat([rsi.shift(k) <= os_ for k in range(4)], axis=1).any(axis=1)
    ob_ago = pd.concat([rsi.shift(k) >= ob for k in range(4)], axis=1).any(axis=1)
    bull = (rsi > rsi.shift(1)) & (rsi.shift(1) < rsi.shift(2))
    bear = (rsi < rsi.shift(1)) & (rsi.shift(1) > rsi.shift(2))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    le = (cross & os_ago & bull & (c <= ema)).to_numpy()
    se = (cross & ob_ago & bear & (c >= ema)).to_numpy()
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le & ~se, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
