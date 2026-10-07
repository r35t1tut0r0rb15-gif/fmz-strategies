"""Single SMA slope, long only: long while the SMA rises, exit when it falls.
Port of FMZ strategy #42451 "Ma单均线趋势交易" (single moving-average trend trading).

Source
    https://www.fmz.com/strategy/42451 (JavaScript, author "ipqhjjybj", FMZ last modified
    2017-06-04 21:55:07). Verbatim copy: original_source.md. Read 2026-09-29.

Original signal (original_source.md lines 96-131)
    kk_MA = TA.MA(records, MA_Length); ma_inc = kk_MA[last] / kk_MA[last-1]
    flat and ma_inc > 1.000001 -> buy all;  long and ma_inc < 0.999999 -> sell all
    Default MA_Length 120.

Interpretation choices
    * The bot polls the forming bar; the port evaluates the same rule on each completed bar t
      (current bar included in the SMA window).
    * The 1e-6 dead band is a dimensionless ratio and is kept as a fixed constant.
    * Long only, as coded. The header comment says "MA up long, MA down short; bitcoin long only";
      the code never shorts, so no short signals are emitted. Opposite entries cannot occur.
    * `trailingPrcnt` (line 27) is declared but never used by the code; not ported.
    * No bar size in the source; FREQ = "bar_size_pending" (rule 2026-10-07: never choose a bar
      size; until 2026-10-07 this port used the old "1h" default). Logic unchanged.
    * Sizing (all-in buy, sell all, minMoney, SlidePrice) is in original_sizing.txt. No costs here.

Marks: bar_size_pending
"""
import pandas as pd

NAME = "fmz_42451_sma_slope_long"
FAMILY = "ma_trend"  # proposed 2026-10-03, user to confirm
FREQ = "bar_size_pending"  # source declares no bar size; set by the project before running
PERIODS_PER_YEAR_OVERRIDE = None
DEAD_BAND = 1e-6

GRID = {"ma_length": [30, 60, 120, 240]}
DEFAULT_PARAMS = {"ma_length": 120}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ma = bars_df["close"].rolling(int(p["ma_length"])).mean()
    ratio = ma / ma.shift(1)
    long_entries = (ratio > 1.0 + DEAD_BAND).fillna(False).astype(bool)
    long_exits = (ratio < 1.0 - DEAD_BAND).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_entries, long_exits, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
