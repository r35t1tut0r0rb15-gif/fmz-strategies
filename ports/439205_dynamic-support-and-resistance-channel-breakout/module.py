"""30-minute bars: a bar whose low is above the last pivot-high resistance (15 / 15) on a volume oscillator (EMA 5 vs 10) above 20 % goes long; a bar whose high is under the last pivot-low support on the same volume test goes short; reversing.
Port of FMZ strategy #439205 "Dynamic Support and Resistance Channel Breakout" (Support and Resistance channel with Breaks p5 [cryptoonchain]).

FMZ source id: 439205

Source
    https://www.fmz.com/strategy/439205 (PineScript v5, FMZ last modified 2024-01-18 12:30:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 153-190), pivots 15 / 15; volume oscillator threshold 20
    highUsePivot = fixnan(pivothigh(15, 15)[1]);  lowUsePivot = fixnan(pivotlow(15, 15)[1]);  osc = 100 * (ema(volume, 5) - ema(volume, 10)) / ema(volume, 10)
    low > highUsePivot and osc > 20 -> entry Long;  high < lowUsePivot and osc > 20 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The break shapes and alerts only plot. Pivots are strict. When both sides signal on one bar the
      later call (short) wins. REVERSAL INTENDED. No sizing code. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, whole-bar breaks of pivot levels on rising volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume oscillator 100 x (ema(v, 5) - ema(v, 10)) / ema(v, 10); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439205_pivot_channel_whole_bar_break_volume_osc_30m_reversal"
FAMILY = "support_resistance"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pivot_len": [15, 10],
    "vol_thresh": [20, 10],
}
DEFAULT_PARAMS = {"pivot_len": 15, "vol_thresh": 20}


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


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, v = bars_df["high"], bars_df["low"], bars_df["volume"]
    n = int(p["pivot_len"])
    hh, hv = _pivot_hit(h, 1, n, n)
    lh, lv = _pivot_hit(lo, -1, n, n)
    res = _fixnan(pd.Series(np.where(hh, hv, np.nan), index=h.index).shift(1))
    sup = _fixnan(pd.Series(np.where(lh, lv, np.nan), index=h.index).shift(1))
    e5, e10 = v.ewm(span=5, adjust=False).mean(), v.ewm(span=10, adjust=False).mean()
    osc = 100 * (e5 - e10) / e10.where(e10 != 0)
    vb = osc > float(p["vol_thresh"])
    long_c = (lo > res) & vb
    short_c = (h < sup) & vb
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (long_c & ~short_c).astype(bool), false, short_c.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
