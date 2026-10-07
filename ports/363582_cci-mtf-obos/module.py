"""CCI on five timeframes (15m, 30m, 1h, 2h, 4h) all at or above +100 goes LONG; all at or below
-100 goes SHORT, as written; decided on the 12-hour chart bar (always in).
Port of FMZ strategy #363582 "CCI MTF Ob+Os".

Source
    https://www.fmz.com/strategy/363582 (PineScript v5, FMZ last modified 2022-05-16 18:12:07).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 75-152), chart 12h; CCI(hlc3, 20); levels +-100
    Fsec(tf, x) = request.security(tf, x, lookahead_off)[1]   (historical bars)
    cciOb = CCI >= 100 on all five timeframes;  cciOs = CCI <= -100 on all five
    cciOb -> entry "Enter Long"; else cciOs -> entry "Enter Short"

Interpretation choices (Pine rules in SURVEY_README.md)
    * All five timeframes are below the 12-hour chart, so request.security returns the last
      intrabar value of each chart bar, and [1] takes the previous chart bar's. The port runs on
      15-minute bars, builds 30m / 1h / 2h / 4h blocks from them (floored on UTC), reads each
      CCI as of the start of the current 12-hour bar, and decides only on the 15-minute bar that
      ends a 12-hour bar (00:00 / 12:00 UTC); the fill is the next 12-hour bar's open, as on the
      12-hour chart.
    * Overbought on every timeframe enters long (and oversold short): kept as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "15min": the lowest requested timeframe; the chart bar (12h) sets decision times.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363582_cci_mtf_extreme_momentum"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # chart 12h (backtest header) reading 15/30/60/120/240-minute values
PERIODS_PER_YEAR_OVERRIDE = None
TIMEFRAMES = (15, 30, 60, 120, 240)  # minutes
CHART_MINUTES = 720

GRID = {
    "cci_len": [14, 20, 30],
}
DEFAULT_PARAMS = {"cci_len": 20, "overbought": 100.0, "oversold": -100.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _block_values(bars, minutes, fn):
    """Aggregate the port's bars into `minutes` blocks (floored on UTC); fn(block_bars) -> values.
    Returns (block end times as int64 ns, values)."""
    key = bars.index.floor(f"{int(minutes)}min")
    agg = bars.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    vals = np.asarray(fn(agg), dtype=float)
    ends = (agg.index + pd.Timedelta(minutes=int(minutes))).asi8
    return ends, vals


def _asof(ends, vals, times):
    """Value of the last block that ended at or before each time (a completed block only)."""
    pos = np.searchsorted(ends, np.asarray(times.asi8), side="right") - 1
    out = np.full(len(pos), np.nan)
    ok = pos >= 0
    out[ok] = vals[pos[ok]]
    return out


def _cci(x, n):
    """ta.cci: (x - sma) / (0.015 * mean absolute deviation)."""
    ma = x.rolling(n).mean()
    mad = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * mad)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["cci_len"])
    idx = bars_df.index
    chart_start = idx.floor(f"{CHART_MINUTES}min")
    ob = np.ones(len(idx), dtype=bool)
    os_ = np.ones(len(idx), dtype=bool)
    for tf in TIMEFRAMES:
        ends, vals = _block_values(bars_df, tf, lambda b: _cci((b["high"] + b["low"] + b["close"]) / 3, n))
        v = _asof(ends, vals, chart_start)
        ob &= v >= p["overbought"]
        os_ &= v <= p["oversold"]
    bar_end = idx + pd.Timedelta(FREQ)
    decide = np.asarray(bar_end == bar_end.floor(f"{CHART_MINUTES}min"))
    return _always_in(ob & decide, os_ & decide, idx)


def portfolio_kwargs(**params):
    return {}
