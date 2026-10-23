"""RedK VADER: close changes over the 2-bar range, weighted by relative volume and averaged into demand / supply energy (WMA 9, average 5, smooth 3), hourly bars: the net energy crossing over zero goes long, otherwise crossing under goes short; reversing.
Port of FMZ strategy #364036 "RedK Volume Accelerated Directional Energy Ratio" (RedK Volume-Accelerated Directional Energy Ratio (VADER v3.0)).

FMZ source id: 364036

Source
    https://www.fmz.com/strategy/364036 (PineScript v5, FMZ last modified 2022-05-18 15:30:50).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 65-212), length 9; DER average 5, WMA, smooth 3; volume Relative, lookback 10
    vola = stoch(volume, highest(volume, 10), lowest(volume, 10), 10) / 100;  c = fixnan(clamp(change(close) / ((highest(2) - lowest(2)) / 2), -1, 1) x vola)
    dem = wma(max(c, 0), 9) / wma(vola, 9);  sup = wma(-min(c, 0), 9) / wma(vola, 9);  anp_s = wma(100 wma(dem, 5) - 100 wma(sup, 5), 3)
    crossover(anp_s, 0) -> entry Long;  else crossunder(anp_s, 0) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * An indicator() script sending strategy orders on FMZ. The relative volume is Pine's stoch of volume
      against its 10-bar highest / lowest (so over 19 bars), na when that range is 0; a zero 2-bar range
      makes the ratio na, which fixnan carries over, as written. The sentiment line is display only.
      REVERSAL INTENDED. No sizing code. The source carries the Mozilla Public License 2.0 notice.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-weighted directional energy zero crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the relative-volume weight of each bar's energy; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_364036_redk_vader9_relative_volume_energy_zero_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [9, 14],
    "vlookbk": [10, 20],
}
DEFAULT_PARAMS = {"length": 9, "vlookbk": 10, "der_avg": 5, "smooth": 3}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def vader(bars_df, length, vlookbk, der_avg, smooth):
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    mn, mx = v.rolling(vlookbk).min(), v.rolling(vlookbk).max()
    lo_mn, hi_mx = mn.rolling(vlookbk).min(), mx.rolling(vlookbk).max()
    vola = (v - lo_mn) / (hi_mx - lo_mn).replace(0.0, np.nan)     # stoch(...) / 100
    r = (h.rolling(2).max() - lo.rolling(2).min()) / 2
    sr = c.diff() / r.replace(0.0, np.nan)
    e = _fixnan(sr.clip(-1, 1) * vola)
    avg_vola = _wma(vola, length)
    dem = _wma(e.clip(lower=0), length) / avg_vola
    sup = _wma((-e).clip(lower=0), length) / avg_vola
    anp = 100 * _wma(dem, der_avg) - 100 * _wma(sup, der_avg)
    return _wma(anp, smooth)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    s = vader(bars_df, int(p["length"]), int(p["vlookbk"]), int(p["der_avg"]), int(p["smooth"]))
    le = (s > 0) & (s.shift(1) <= 0)
    se = (s < 0) & (s.shift(1) >= 0) & ~le
    false = pd.Series(False, index=s.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
