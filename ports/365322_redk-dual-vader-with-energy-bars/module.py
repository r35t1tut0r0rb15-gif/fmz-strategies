"""RedK VADER v4 (the v3 energy with the author's v4 defaults: WMA 10, average 5, smooth 3, relative volume over 20 bars), 45-minute bars: the net energy crossing over zero goes long, otherwise crossing under goes short; reversing.
Port of FMZ strategy #365322 "RedK Dual VADER with Energy Bars" (RedK Dual VADER with Energy Bars (VADER-DEB v4.0)).

FMZ source id: 365322

Source
    https://www.fmz.com/strategy/365322 (PineScript v5, FMZ last modified 2022-05-24 11:49:07).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 60-228), length 10; DER average 5, WMA, smooth 3; volume Relative, lookback 20
    the VADER energy of #364036 with length 10 and lookback 20;  crossover(anp_s, 0) -> entry Long;  else crossunder(anp_s, 0) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same calculation as #364036 (the author states no core change in v4; the energy bars and the
      sentiment area are display only), with this script's defaults; a near twin under rule 7. REVERSAL
      INTENDED. No sizing code. The source carries the Mozilla Public License 2.0 notice. FREQ = "45min"
      from the backtest header.

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

NAME = "fmz_365322_redk_vader10_relative_volume20_energy_zero_cross_reversal"
FAMILY = "momentum_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [10, 20],
    "vlookbk": [20, 10],
}
DEFAULT_PARAMS = {"length": 10, "vlookbk": 20, "der_avg": 5, "smooth": 3}


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
