"""WMA 7 / 9 cross-ups with the RSI 14 under 40, 3-hour bars, long only: the cross up buys with a 20-point stop and a 40-point target from the fill (0.000476 / 0.000952 at BTC 42000).
Port of FMZ strategy #458059 "Weighted Moving Average and Relative Strength Index Crossover Strategy with Risk Management Optimization System" (Estrategia de Cruce de WMA Optimizada con Stop Loss, Take Profit y RSI (Solo Long)).

FMZ source id: 458059

Source
    https://www.fmz.com/strategy/458059 (PineScript v5, FMZ last modified 2024-07-29 16:07:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 247-288), WMA 7 / 9 (labelled 14); RSI 14 under 40; target 40 / stop 20 points from the average price
    crossover(wma7, wma9) and rsi < 40 -> entry Long;  long: exit(limit = avg + 40, stop = avg - 20)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The points are price amounts added to the average price: read against BTC near 42000 like other
      price units (#440456), they are ported as the fixed fractions 20 / 42000 and 40 / 42000 of the
      fill, active from the fill bar (#440797). Long only. Stop module: portfolio_kwargs {} (driver
      D4). Stops on 3-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest
      header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point bracket as fractions of 42000.
    2 generic: PASS, WMA cross-ups in a weak RSI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458059_wma7_9_cross_up_rsi40_point_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_frac": [0.000476, 0.01],
    "tp_frac": [0.000952, 0.02],
}
DEFAULT_PARAMS = {"sl_frac": 0.000476, "tp_frac": 0.000952}


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


def _wma(x, n):
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def simulate(bars_df, **params):
    c = bars_df["close"]
    a, b = _wma(c, 7), _wma(c, 9)
    r = _rsi(c, 14)
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 40)
    false = pd.Series(False, index=bars_df.index)
    return le, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
