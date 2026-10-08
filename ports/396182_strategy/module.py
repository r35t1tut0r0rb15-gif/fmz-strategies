"""定投止盈 (Zer3192): the open crossing above the close (a red bar after a green one) goes long; a
take-profit a fixed distance above the entry closes it. Long only, no stop.
Port of FMZ strategy #396182 "定投止盈".

Source
    https://www.fmz.com/strategy/396182 (PineScript v4, author Zer3192, FMZ last modified
    2023-01-29 09:49:34). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 27-49), take-profit value 3 (price units)
    crossover(open, close) -> entry long (ignored while long, pyramiding 0)
    exit(limit = avg price + 3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the +3 target is in price units. It becomes tp_atr x ATR(14) at the signal bar,
      a tp_stop fraction shifted one bar inside stops(); vbt re-bases it on the fill price.
    * The "max loss %" input is declared but never used (no stop), as written.
    * Long only, as written (rule 6); upon_opposite_entry="ignore". Repeated signals while long
      are ignored by the engine as by Pine.
    * No bar size in the source: FREQ = "bar_size_pending" (rule 1, 2026-10-07).

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_396182_red_turn_long_tp"
FAMILY = "candle_pattern"  # proposed 2026-10-07, user to confirm
FREQ = "bar_size_pending"  # no bar size in the source (rule 1, 2026-10-07)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "tp_atr": [0.5, 1.0, 2.0],
}
DEFAULT_PARAMS = {"tp_atr": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _entries(bars_df):
    o, c = bars_df["open"], bars_df["close"]
    return ((o > c) & (o.shift(1) <= c.shift(1))).to_numpy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    le = _entries(bars_df)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le = pd.Series(_entries(bars_df), index=bars_df.index)
    tp = (p["tp_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]).where(le)
    return {"tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
